#map_metric.py
#! python3
"""Automate printings maps of congestion metrics using PyQGIS

This command line utility can automate cycling over multiple years, hours of
the day, and metrics to load layers from the PostgreSQL DB, add them to a
template map and then print them to a png.

usage: map_metric.py [-h] -r YYYYMM YYYYMM
                     (-p TIMEPERIOD [TIMEPERIOD ...] | -i HOURS_ITERATE HOURS_IT
ERATE)
                     [-d DBSETTING] [-t TABLENAME]
                     {b,t} [{b,t} ...] {year,quarter,month}

Produce maps of congestion metrics (tti, bti) for different aggregation
periods, timeperiods, and aggregation levels

positional arguments:
  {b,t}                 Map either Buffer Time Index, Travel Time Index or
                        both e.g. b, t, or 'b t'
  {year,quarter,month}  Aggregation level to be used

optional arguments:
  -h, --help            show this help message and exit
  -r YYYYMM YYYYMM, --range YYYYMM YYYYMM
                        Range of months (YYYYMM) to operate overfrom startdate
                        to enddate. Accepts multiple pairs
  -p TIMEPERIOD [TIMEPERIOD ...], --timeperiod TIMEPERIOD [TIMEPERIOD ...]
                        Timeperiod of aggregation, use 1 arg for 1 hour or 2
                        args for a range
  -i HOURS_ITERATE HOURS_ITERATE, --hours_iterate HOURS_ITERATE HOURS_ITERATE
                        Hours to iterate over
  -d DBSETTING, --dbsetting DBSETTING
                        Filename with connection settings to the
                        database(default: opens default.cfg)
  -t TABLENAME, --tablename TABLENAME
                        Table containing metrics congestion.metrics
"""

#TODO import stuff
import sys
import logging
import calendar
#qgis imports
QGIS_CONSOLE = True #For testing in console
if QGIS_CONSOLE:
    from qgis.utils import iface
else:
    from qgis.core import *
    from parsing_utils import parse_args, _validate_multiple_yyyymm_range, _get_timerange, format_fromto_hr

from congestion_mapper import CongestionMapper
from qgis.PyQt.QtXml import QDomDocument
from qgis.gui import QgsMapCanvasLayer

SQLS = {'year':"""(
SELECT row_number() OVER (PARTITION BY metrics.agg_period ORDER BY metrics.{metric} DESC) AS "Rank",
    tmc_from_to_lookup.street_name AS "Street",
    gis.twochar_direction(inrix_tmc_tor.direction) AS "Dir",
    tmc_from_to_lookup.from_to AS "From - To",
    to_char(metrics.{metric}, '0D99'::text) AS "{metric_name}",
    inrix_tmc_tor.geom
FROM congestion.metrics
JOIN congestion.aggregation_levels USING (agg_id)
JOIN gis.inrix_tmc_tor USING (tmc)
JOIN gis.tmc_from_to_lookup USING (tmc)
WHERE inrix_tmc_tor.sum_miles > 0.124274 AND aggregation_levels.agg_level = 'year'
AND metrics.timeperiod = {timeperiod} AND metrics.agg_period = {agg_period}::DATE
ORDER BY metrics.{metric} DESC LIMIT 50)"""#,
    #'quarter':''''''
    #'month':''''''
}

METRICS = {'b':{'sql_acronym':'bti',
                'metric_name':'Buffer Time Index',
                'metric_attr':'Least Reliable',
                'stat_description':'Buffer Time Index = (95th percentile Time - Median Time)/(Median Time)'
               },
           't':{'sql_acronym':'tti',
                'metric_name': 'Travel Time Index',
                'metric_attr':'Most Congested',
                'stat_description':'Travel Time Index = Average Travel Time / Free Flow Travel Time'
               }
          }

COMPOSER_LABELS = {'map_title': '{agg_period} Top 50 {metric_attr} Road Segments',
                   'time_period': '{period_name} ({from_to_hours})',
                   'stat_description': '{stat_description}'}
BACKGROUND_LAYERNAMES = [u'CENTRELINE_WGS84', u'to']

def _new_uri(dbset):
    '''Create a new URI based on the database settings and return it

    Args:
        dbset: dictionary of database connection settings
    
    Returns:
        PyQGIS uri object'''
    uri = QgsDataSourceURI()
    uri.setConnection(dbset['host'], "5432", dbset['database'], dbset['user'], dbset['password'])
    return uri

def _get_agg_layer(uri, agg_level=None, agg_period=None, timeperiod=None,
                   layername=None, metric=None, metric_name= None):
    '''Create a QgsVectorLayer from a connection and specified parameters

    Args:
        uri: PyQGIS uri object
        agg_level: string representing aggregation level, key to SQLS dict
        agg_period: the starting aggregation date for the period as a string
            digestible by PostgreSQL into a DATE
        timeperiod: string representing a PostgreSQL timerange
        layername: string name to give the layer

    Returns:
        QgsVectorLayer from the specified sql query with provided layername'''
    if agg_level not in SQLS:
        raise ValueError('Aggregation level: {agg_level} not implemented'.format(
            agg_level=agg_level))
    
    sql = SQLS[agg_level]
    sql = sql.format(timeperiod=timeperiod, agg_period=agg_period, metric=metric, metric_name=metric_name)
    uri.setDataSource("", sql, "geom", "", "Rank")
    return QgsVectorLayer(uri.uri(False), layername, 'postgres')

def _get_agg_period(agg_level, year, month):
    '''Create a text representation of the aggregation period
    
    Takes the aggregation level, the aggregation period's year and month, then
    returns a text representation of the aggregation period.
     
    Args:
        agg_level (str): aggregation Level
        year (int): the aggregation period's year
        month (int): the aggregation period's month
    Returns:
        a text representation of the aggregation period based on the 
        aggregation level and the provided year and month
    Raises:
        NotImplementedError: if the agg_level is not hardcoded in the function 
            logic {'year','quarter','month'}
    '''
    agg_period = ''
    if agg_level == 'year':
        agg_period = str(year)
    elif agg_level == 'quarter':
        q = int(month/3) + 1
        agg_period = str(year) + ' Q' + str(q)
    elif agg_level == 'month':
        month_text = calendar.month_name[month]
        agg_period = month_text + ' ' + str(year)
    else:
        raise NotImplementedError('No support for {agg_level}'.format({'agg_level':agg_level}))
    return agg_period


def update_labels(composition, labels_dict = COMPOSER_LABELS, labels_update = None):
    '''Change the labels in the QgsComposition using a dictionary of update values
    
    Iterates over the keys (label ids) and values (strings to update) of the labels_dict
    Finds the corresponding element of the composition, and updates it based on keys and 
    values provided in labels_update.
    
    Args:
        composition: the QgsComposition
        labels_dict: dictionary of labels to change of form 
            {'label_id':'label_text to {update_section}'}
        labels_update: dictionary of values to update labels with
            format: {'update_section':'update_value'}
    Returns:
        None'''
    for label_id, label_text in labels_dict.items():
        composition.getComposerItemById(label_id).setText(label_text.format(**labels_update))
    

def load_print_composer(template, console=True):
    '''Load a print composer template from provided filename argument
    
    Args:
        template: readable .qpt template filename
        console: boolean if method is used in QGIS console
        
    Returns:
        myComposition: a QgsComposerView loaded from the provided template
        --mapSettings: a QgsMapSettings object associated with myComposition'''
    # Load template from filename
    myDocument = QDomDocument()
    with open(template, 'r') as templateFile:
        myTemplateContent = templateFile.read()
        myDocument.setContent(myTemplateContent)
    composerView = None
    
    if console:
        composerView = iface.createNewComposer()
        composerView.composition().loadFromTemplate(myDocument)
        myComposition = composerView.composition()
        mapSettings = myComposition.mapSettings()
    else:
        raise NotImplementedError('More work needs to be done for standalone')
        canvas = QgsMapCanvas()
        # Load our project
        QgsProject.instance().read(QFileInfo(project_path))
        bridge = QgsLayerTreeMapCanvasBridge(
            QgsProject.instance().layerTreeRoot(), canvas)
        bridge.setCanvasLayers()
        mapSettings = QgsMapSettings()
        myComposition = QgsComposition(mapSettings)
        myComposition.loadFromTemplate(myDocument)
    return {'QgsComposition': myComposition,
            'QgsMapSettings': mapSettings,
            'QgsComposerView': composerView}

def get_background_layers(mapregistry, layernamelist):
    '''Return background layers'''
    
    layers = [map_registry.mapLayersByName(name)[0] for name in layernamelist]
    layerslist = [QgsMapCanvasLayer(layer) for layer in layers]
    return layerslist

if __name__ == '__main__':
    #Configure logging
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)
    LOGGER = logging.getLogger(__name__)
    
    ARGS = parse_args(sys.argv[1:])
    
    import configparser
    CONFIG = configparser.ConfigParser()
    CONFIG.read(ARGS.dbsetting)
    dbset = CONFIG['DBSETTINGS']

    try:
        YEARS = _validate_multiple_yyyymm_range(ARGS.years)
    except ValueError as err:
        LOGGER.critical(str(err))
        sys.exit(2)
        
    #TODO stylepath
    stylepath = "K:\\Big Data Group\\Data\\GIS\\Congestion_Reporting\\top50style.qml"
    template = 'K:\\Big Data Group\\Data\\GIS\\Congestion_Reporting\\top_50_template.qpt'
    
    gui_flag = True
    app = QgsApplication(sys.argv, gui_flag)
    app.initQgis()
    
    mapper = CongestionMapper(LOGGER, dbset, stylepath, templatepath, projectfile, ARGS.agg_level)
        
    for m in ARGS.metric:
        mapper.set_metric(m)
        
        for year in YEARS:
            for month in YEARS[year]:
                yyyymmdd = get_yyyymmdd(year, month)
                if ARGS.hours_iterate:
                    hour_iterator = range(ARGS.hours_iterate[0], ARGS.hours_iterate[1]+1)
                else:
                    hour_iterator = range(ARGS.timeperiod[0], ARGS.timeperiod[0]+1)
                for hour1 in hour_iterator:
                    
                    hour2 = hour1 + 1 if ARGS.hours_iterate else ARGS.timeperiod[1]
                    timerange = _get_timerange(hour1, hour2)
                    layername = year + month + 'h' + hour1 + ARGS.agg_level
                    
                    mapper.load_agg_layer(yyyymmdd, timerange, layername)
                    update_values = {'agg_period': _get_agg_period(ARGS.agg_level, year, month),
                                     'period_name': ARGS.periodname,
                                     'from_to_hours': format_fromto_hr(hour1, hour2), 
                                     'stat_description': mapper.metric['stat_description'],
                                     'metric_attr': mapper.metric['metric_attr']
                                    }
                    mapper.update_labels(labels_update = update_values)
                    
                    mapper.update_table()
                    mapper.print_map( )
                    mapper.clear_layer()
    mapper.project.clear()
    app.exitQgis()
            

elif QGIS_CONSOLE:
    import StringIO
    from datetime import time
    
    buf = StringIO.StringIO(s_config)
    config = ConfigParser.ConfigParser()
    config.readfp(buf)
    dbset = config._sections['DBSETTINGS']
    URI = _new_uri(dbset)
    
    map_registry = QgsMapLayerRegistry.instance()
    template = "K:\\Big Data Group\\Data\\GIS\\Congestion_Reporting\\top_50_template.qpt"
    stylepath = "K:\\Big Data Group\\Data\\GIS\\Congestion_Reporting\\top50style.qml"
    
    printcomposer = load_print_composer(template)

    background_layers = get_background_layers(map_registry, BACKGROUND_LAYERNAMES)
    
    # Setting up variables for iteration
    agg_level = 'year'
    metric = METRICS['b']
    yyyymmdd = "'2015-01-01'"
    year = '2015'
    month = '01'
    hour1 = 17
    hour2 = 18
    periodname = 'PM Peak'
    timerange = _get_timerange(hour1, hour2)
    layername = '2015_pm_reliable'
    
    # Begin iteration section
    layer = _get_agg_layer(URI, agg_level=agg_level,
                           agg_period=yyyymmdd,
                           timeperiod=timerange,
                           metric=metric['sql_acronym'],
                           layername=layername,
                           metric_name=metric['metric_name'])
    
    
    map_registry.addMapLayer(layer)
    layer.loadNamedStyle(stylepath)
    
    layerslist = [QgsMapCanvasLayer(layer)] + background_layers
    iface.mapCanvas().setLayerSet(layerslist)
    iface.mapCanvas().refresh()
    
    update_values = {'agg_period': _get_agg_period(agg_level, year, month),
                     'period_name': periodname,
                     'from_to_hours': format_fromto_hr(hour1, hour2), 
                     'stat_description': metric['stat_description'],
                     'metric_attr': metric['metric_attr']
                    }
    update_labels(printcomposer['QgsComposition'], labels_update = update_values)
    table = printcomposer['QgsComposition'].getComposerItemById('table').multiFrame()
    table.setVectorLayer(layer)
    printcomposer['QgsComposition'].refreshItems()
    image = printcomposer['QgsComposition'].printPageAsRaster(0)
    image.save(r"C:\Users\rdumas\Desktop\test.png")
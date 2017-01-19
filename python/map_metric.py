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
    lib_path = r"C:\Users\rdumas\Documents\GitHub\bdit_congestion\congestion_mapping\python"
    sys.path.append(lib_path)
    from parsing_utils import validate_multiple_yyyymm_range
else:
    from qgis.core import *
    from parsing_utils import parse_args

from parsing_utils import get_timerange, format_fromto_hr, get_yyyymmdd
from congestion_mapper import CongestionMapper

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

    #TODO stylepath
    stylepath = "K:\\Big Data Group\\Data\\GIS\\Congestion_Reporting\\top50style.qml"
    template = 'K:\\Big Data Group\\Data\\GIS\\Congestion_Reporting\\top_50_template.qpt'
    
    gui_flag = True
    app = QgsApplication([], gui_flag)
    app.initQgis()
    
    mapper = CongestionMapper(LOGGER, dbset, stylepath, templatepath, projectfile, ARGS.Aggregation)
        
    for m in ARGS.metric:
        mapper.set_metric(m)
        for year in args.years:

            for month in YEARS[year]:
                yyyymmdd = get_yyyymmdd(year, month)
                if ARGS.hours_iterate:
                    hour_iterator = range(ARGS.hours_iterate[0], ARGS.hours_iterate[1]+1)
                else:
                    hour_iterator = range(ARGS.timeperiod[0], ARGS.timeperiod[0]+1)
                for hour1 in hour_iterator:
                    
                    hour2 = hour1 + 1 if ARGS.hours_iterate else ARGS.timeperiod[1]
                    timerange = get_timerange(hour1, hour2)
                    layername = year + month + 'h' + hour1 + ARGS.Aggregation
                    
                    mapper.load_agg_layer(yyyymmdd, timerange, layername)
                    update_values = {'agg_period': _get_agg_period(ARGS.Aggregation, year, month),
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
    import ConfigParser
    from datetime import time
    
    buf = StringIO.StringIO(s_config)
    config = ConfigParser.ConfigParser()
    config.readfp(buf)
    dbset = config._sections['DBSETTINGS']
    
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)
    LOGGER = logging.getLogger(__name__)
    
    templatepath = "K:\\Big Data Group\\Data\\GIS\\Congestion_Reporting\\top_50_template.qpt"
    stylepath = "K:\\Big Data Group\\Data\\GIS\\Congestion_Reporting\\top50style.qml"
    print_directory = r"C:\Users\rdumas\Documents\test\\"
    #print_format = ''
    
    # Setting up variables for iteration
    agg_level = 'year' #['year','quarter','month']
    metrics = ['b'] #['b','t'] for bti, tti
    yyyymmrange = [['201501', '201501']] 
    #for multiple ranges
    #yyyymmrange = [['201203', '201301'],['201207', '201209']] 
    
    years = validate_multiple_yyyymm_range(yyyymmrange, agg_level)
    hours_iterate = []
    timeperiod = [17,18]
    periodname = 'PM Peak'
    
    mapper = CongestionMapper(LOGGER, dbset, stylepath, templatepath,
                              agg_level, console = True, iface = iface)

    for m in metrics:
        mapper.set_metric(m)
        for year in years:

            for month in years[year]:
                yyyymmdd = get_yyyymmdd(year, month)
                if hours_iterate:
                    hour_iterator = range(hours_iterate[0], hours_iterate[1]+1)
                else:
                    hour_iterator = range(timeperiod[0], timeperiod[0]+1)
                for hour1 in hour_iterator:
                    
                    hour2 = hour1 + 1 if hours_iterate else timeperiod[1]
                    timerange = get_timerange(hour1, hour2)
                    if periodname is not None:
                        timeval = periodname.replace(' ','').lower()
                    else:
                        timeval = str(hour1)
                    layername = str(year) + str(month) + 'h' + timeval + agg_level
                    
                    mapper.load_agg_layer(yyyymmdd, timerange, layername)
                    mapper.update_canvas(iface = iface)
                    update_values = {'agg_period': _get_agg_period(agg_level, year, month),
                                     'period_name': periodname,
                                     'from_to_hours': format_fromto_hr(hour1, hour2), 
                                     'stat_description': mapper.metric['stat_description'],
                                     'metric_attr': mapper.metric['metric_attr']
                                    }
                    #TODO Fix this hack
                    mapper.update_labels(labels_dict = CongestionMapper.COMPOSER_LABELS, labels_update = update_values)
                    
                    mapper.update_table()
                    mapper.print_map(print_directory + layername + '.png' )
                    #mapper.clear_layer()

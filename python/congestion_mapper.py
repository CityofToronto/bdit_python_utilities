#! python3
'''Object definition for congestion mapping
'''

class congestion_mapper( object ):
    '''Holds settings for iterating over multiple congestion maps
    '''
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
    
    def __init__(self, logger, dbsettings, stylepath, templatepath, projectfile = None, console = False):
        self.uri = _new_uri(dbsettings)
        self.stylepath = stylepath
        self.template = QDomDocument()
        with open(templatepath, 'r') as templateFile:
            templateContent = templateFile.read()
            self.template.setContent(myTemplateContent)
        
        if projectfile:
            #Open project
        
        printcomposer = load_print_composer(console=console)
        self.composition = printcomposer['QgsComposition']
        self.map_settings = printcomposer['QgsMapSettings']
        self.composer_view = printcomposer['QgsComposerView']
            
        self.map_registry = QgsMapLayerRegistry.instance()
        self.background_layers = get_background_layers(map_registry, BACKGROUND_LAYERNAMES)
    

    @staticmethod
    def _new_uri(dbset):
    '''Create a new URI based on the database settings and return it

    Args:
        dbset: dictionary of database connection settings
    
    Returns:
        PyQGIS uri object'''
    uri = QgsDataSourceURI()
    uri.setConnection(dbset['host'], "5432", dbset['database'], dbset['user'], dbset['password'])
    return uri

    def load_print_composer(console=True):
        '''Load a print composer template from provided filename argument

        Args:
            template: readable .qpt template filename
            console: boolean if method is used in QGIS console

        Returns:
            myComposition: a QgsComposerView loaded from the provided template
            --mapSettings: a QgsMapSettings object associated with myComposition'''
        
        composerView = None

        if console:
            composerView = iface.createNewComposer()
            composerView.composition().loadFromTemplate(self.template)
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
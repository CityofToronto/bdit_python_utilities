#! python3
"""Object definition for congestion mapping
"""

from datetime import time
from qgis.core import QgsVectorLayer
from iteration_mapper import IteratingMapper
from parsing_utils import get_yyyymmdd

class CongestionMapper( IteratingMapper ):
    """Holds settings for iterating over multiple congestion maps
    
    Inherits from IteratingMapper
    
    Attributes:
        agg_level: The aggregation level to use
        metric: The metric currently being mapped.
        METRICS: static dictionary holding strings for each metric to be used to update 
            composer levels or in SQL scripts
        COMPOSER_LABELS: static dictionary holding base string labels for the print 
            composer to be updated for each map
        BACKGROUND_LAYERS: static list holding the names of the background layers to be 
            displayed on the map
    """

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
    IteratingMapper.COMPOSER_LABELS = COMPOSER_LABELS
    BACKGROUND_LAYERNAMES = [u'CENTRELINE_WGS84', u'to']
    IteratingMapper.BACKGROUND_LAYERNAMES = BACKGROUND_LAYERNAMES
    
    
    def __init__(self, logger, dbsettings, stylepath, templatepath, agg_level, *args, **kwargs):
        """Initialize CongestionMapper and parent object
        """
        super(CongestionMapper, self).__init__(logger, dbsettings, stylepath, templatepath, *args, **kwargs)
        self.agg_level = agg_level
        self.metric = None
        self.background_layers = self.get_background_layers(self.BACKGROUND_LAYERNAMES)
    
    def load_agg_layer(self, year, month, time1, time2, yyyymmdd=None, 
                   layername=None):
        """Create a QgsVectorLayer from a connection and specified parameters

        Args:
            yyyymmdd: the starting aggregation date for the period as a string
                digestible by PostgreSQL into a DATE
            timeperiod: string representing a PostgreSQL timerange
            layername: string name to give the layer

        Returns:
            QgsVectorLayer from the specified sql query with provided layername"""
        
        if time1 == time2:
            raise ValueError('2nd time parameter {time2} must be at least 1 hour after first parameter {time1}'.format(time1=time1, time2=time2))
        
        starttime = time(int(time1)).isoformat()

        #If the second time is 24, aka midnight, replace with maximum possible time for the range
        if time2 == 24:
            endtime = '24:00'
        else:
            endtime = time(int(time2)).isoformat()

        if starttime > endtime:
            raise ValueError('start time {starttime} after end time {endtime}'.format(starttime=starttime, endtime=endtime))
        
        sql = '''(SELECT (congestion.map_metrics('{agg_lvl}', '{agg_period}'::DATE, '{starttime}'::TIME,
         '{endtime}'::TIME, '{metric}', '{metric_name}')).* )''' 
        sql = sql.format(agg_lvl=self.agg_level,
                         starttime=starttime, 
                         endtime=endtime
                         agg_period=get_yyyymmdd(year, month),
                         metric=self.metric['sql_acronym'],
                         metric_name=self.metric['metric_name'])
        # params: (schema, 'tablename', geom column, WHERE clause, gid)
        self.uri.setDataSource("", sql, "geom", "", "Rank")
        self.load_layer(layername, 'postgres')
        
            
    def set_metric(self, metric_id):
        """Set the metric for mapping based on the provided key
        """
        if metric_id not in self.METRICS:
            raise ValueError('{metric_id} is unsupported'.format(metric_id=metric_id))
        self.metric = self.METRICS[metric_id]

    def update_table(self):
        """Update the table in the composition to use current layer
        """
        table = self.composition.getComposerItemById('table').multiFrame()
        table.setVectorLayer(self.layer)
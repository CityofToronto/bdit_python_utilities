#map_metric.py
#! python2
"""Automate printings maps of congestion metrics using PyQGIS


###############################################

WARNING 

This is abstract example code to base subclassing 
iteration_mapper on. It **won't** work if you run 
it as is.

WARNING

###############################################
"""


import sys
import logging
import calendar
from qgis.utils import iface
from iteration_mapper import IterationMapper

#If run from the QGIS console
if __name__ == '__console__':
    import StringIO
    import ConfigParser
    
    # Variables to change
    # Paths
    templatepath = "K:\\Big Data Group\\Data\\GIS\\Congestion_Reporting\\top_50_template.qpt"
    stylepath = "K:\\Big Data Group\\Data\\GIS\\Congestion_Reporting\\top50style.qml"
    print_directory = r"C:\Users\rdumas\Documents\test\\"
    #print_format = ''
    
    # Setting up variables for iteration
    yyyyrange = [2015, 2016] 
    # Copy and paste your db.cfg file between the quotes
    s_config = '''
    '''
    
    # The script can take it from here.
    
    buf = StringIO.StringIO(s_config)
    config = ConfigParser.ConfigParser()
    config.readfp(buf)
    dbset = config._sections['DBSETTINGS']
    
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)
    LOGGER = logging.getLogger(__name__)

    
    sql = '''SELECT gid, geom, metric 
        FROM your_table 
        WHERE year = {year}
        '''
    
    mapper = IterationMapper(LOGGER, dbset, stylepath, templatepath, sql, console = True, iface = iface)

    
    for year in yyyyrange:
        layername = str(year) + ' Test Layer'

        #mapper.uri.setDataSource() needs to be called
        sql_params = {'year':year}
        mapper.load_sql_layer(layername, sql_params)
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

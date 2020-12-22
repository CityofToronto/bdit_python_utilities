# -*- coding: utf-8 -*-
"""
Version 0.8.0 


"""
from psycopg2 import connect
import psycopg2.sql as pg
import pandas.io.sql as pandasql
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.ticker as ticker
import geopandas as gpd
import os
import shapely
import seaborn as sns
from shapely.geometry import Point
import matplotlib.font_manager as font_manager
import numpy as np

def fake_chart(data_in, xlab,**kwargs):
    """Creates nothing. This is just a test. 
       
    Parameters
    -----------
    data : dataframe
        Data for the fake chart. The dataframe must have 2 columns
    xlab : str
        Label for the x axis.
    xmax : int, optional, default is the max s value
        The max value of the y axis
    xmin : int, optional, default is 0
        The minimum value of the x axis
    precision : int, optional, default is -1
        Decimal places in the annotations
        
    xinc : int, optional
        The increment of ticks on the x axis.
      
    Returns 
    --------
    fig
        Matplotlib fig object
    ax 
        Matplotlib ax object
            
    """
    print(list(data_in))
        
    return "returning fake chart" 

"""
Fake Chart
==================

Makes an example of a fake chart.
"""

from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd 
import configparser
from psycopg2 import connect
import psycopg2.sql as pg
import pandas.io.sql as pandasql
import numpy as np 
import datetime
import math
import rick
import geopandas as gpd
import os
import shapely
from shapely.geometry import Point
# os.environ["PROJ_LIB"]=r"C:\Users\rliu4\AppData\Local\Continuum\anaconda3\Library\share"
import importlib
import matplotlib.ticker as ticker
import matplotlib.font_manager as font_manager

################################
#Define the global variables 
#---------------------------
class font:
    """
    Class defining the global font variables for all functions.
    
    """
    
    leg_font = font_manager.FontProperties(family='Libre Franklin',size=9)
    normal = 'Libre Franklin'
    semibold = 'Libre Franklin SemiBold'


class colour:
    """
    Class defining the global colour variables for all functions.
    
    """
    purple = '#660159'
    grey = '#7f7e7e'
    light_grey = '#777777'
    cmap = 'YlOrRd'

################################
#Define the chart
#----------------
#
#This creates chart fake_chart 
def fake_chart(data_in, xlab,**kwargs):
        """Creates a bar chart
        
        Parameters
        -----------
        data : dataframe
            Data for the bar chart. The dataframe must have 2 columns, the first 
            representing the y ticks, and the second representing the data
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
        data = data_in.copy(deep=True)
        
        data.columns = ['name', 'values1']
        
        xmin = kwargs.get('xmin', 0)
        xmax = kwargs.get('xmax', None)
        precision = kwargs.get('precision', 0)
        
        xmax_flag = True
        if xmax == None:
            xmax = data['values1'].max()
            xmax_flag = False

        delta = (xmax - xmin)/4
        i = 0
        while True:
            if delta < 10:
                break
            delta /= 10
            i += 1
        xinc = kwargs.get('xinc', int(round(delta+1)*pow(10,i)))

        if xmax_flag == True:
            upper = xmax
        else:
            upper = int(4*xinc+xmin)
        
        ind = np.arange(len(data))

        fig, ax = plt.subplots()
        fig.set_size_inches(6.1, len(data)*0.7)
        ax.grid(color='k', linestyle='-', linewidth=0.25)
        p2 = ax.barh(ind, data['values1'], 0.75, align='center', color = colour.purple)
        ax.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))

        ax.xaxis.grid(True)
        ax.yaxis.grid(False)
        ax.set_yticks(ind)
        ax.set_xlim(0,upper)
        ax.set_yticklabels(data['name'])
        ax.set_xlabel(xlab, horizontalalignment='left', 
                      x=0, labelpad=10, fontname = font.normal, 
                      fontsize=10, fontweight = 'bold')

        ax.set_facecolor('xkcd:white')
        j=0
        
        if precision < 1:
            data['values1'] = data['values1'].astype(int)

        j=0
        for i in data['values1']:
            if i < 0.1*upper:
                ax.annotate(str(format(round(i,precision), ',')), 
                            xy=(i+0.015*upper, j-0.05), 
                            ha = 'left', color = 'k', fontname = font.normal, fontsize=10)
            else:
                ax.annotate(str(format(round(i,precision), ',')), 
                            xy=(i-0.015*upper, j-0.05), 
                            ha = 'right', color = 'w', fontname = font.normal, fontsize=10)
            j=j+1

        
        plt.xticks(range(xmin,upper+int(0.1*xinc), xinc), fontname = font.normal, fontsize =10)
        plt.yticks( fontname = font.normal, fontsize =10)
        
        return fig, ax


################################
#Data Collection
#----------------
#
#This creates a test dataframe to use
pass_data = {'cat': ['PTC','Taxi',  'Trip Making Population'],
        'TTC Pass': [22,16,16],
        }

transit_pass = pd.DataFrame(pass_data,columns= ['cat', 'TTC Pass'])
transit_pass  = transit_pass .reindex(index=transit_pass .index[::-1])

fig, ax = fake_chart(transit_pass, xlab='Trips')

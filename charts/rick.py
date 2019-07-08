# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 17:01:30 2019

@author: rliu4
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
from shapely.geometry import Point

#shapely workaround for windows
#os.environ["PROJ_LIB"]=r"C:\Users\rliu4\AppData\Local\Continuum\anaconda3\Library\share"

class colour:
    purple = '#660159'
class geo:
    
    def ttc(con):
        query = '''
        
        SELECT * FROM gis.subway_to
        
        '''
        ttc = gpd.GeoDataFrame.from_postgis(query, con, geom_col='geom')
        ttc = ttc.to_crs({'init' :'epsg:3857'})
        
        for index, row in ttc.iterrows():
            rotated = shapely.affinity.rotate(row['geom'], angle=-17, origin = Point(0, 0))
            ttc.loc[index, 'geom'] = rotated  
        
        return ttc
    
    def island(con):
        query = '''

        SELECT 
        geom
        FROM tts.zones_tts06
        WHERE gta06 = 81

        '''

        island =  gpd.GeoDataFrame.from_postgis(query, con, geom_col='geom')
        island  = island.to_crs({'init' :'epsg:3857'})

        for index, row in island.iterrows():
            rotated = shapely.affinity.rotate(row['geom'], angle=-17, origin = Point(0, 0))
            island.loc[index, 'geom'] = rotated

        return island
    
class charts:
    
    def chloro_map(con, df, lower, upper, title, **kwargs):
        
        subway = kwargs.get('subway', False)
        island = kwargs.get('island', True)
        cmap = kwargs.get('cmap', 'YlOrRd')
        unit = kwargs.get('unit', None)
        nbins = kwargs.get('nbins', 2)
        
        df.columns = ['geom', 'values']
        light = '#d9d9d9'

        fig, ax = plt.subplots()
        fig.set_size_inches(6.69,3.345)
         
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        ax.set_axis_off()
    
        mpd = df.plot(column='values', ax=ax, vmin=lower, vmax=upper,  cmap = cmap, edgecolor = 'w', linewidth = 0.5)
        
        if island == False:
            island_grey = geo.island(con)
            island_grey.plot(ax=ax, edgecolor = 'w', linewidth = 4,  color = light)
            island_grey.plot(ax=ax, edgecolor = 'w', linewidth = 0,  color = light)
         
        if subway == True:
            ttc_df = geo.ttc(con)
            line = ttc_df.plot( ax=ax, linewidth =4, color = 'w', alpha =0.6) # ttc subway layer
            line = ttc_df.plot( ax=ax, linewidth =2, color = 'k', alpha =0.4) # ttc subway layer
    
         
        props = dict(boxstyle='round', facecolor='w', alpha=0)
        plt.text(0.775, 0.37, title, transform=ax.transAxes, wrap = True, fontsize=7, fontname = 'Libre Franklin SemiBold',
                verticalalignment='bottom', bbox=props, fontweight = 'bold') # Adding the Legend Title
         
        
        cax = fig.add_axes([0.718, 0.16, 0.01, 0.22]) # Size of colorbar
         
        rect = patches.Rectangle((0.76, 0.01),0.235,0.43,linewidth=0.5, transform=ax.transAxes, edgecolor=light,facecolor='none')
        ax.add_patch(rect)
        
        ax.margins(0.1)
         
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=lower, vmax=upper))
        sm._A = []
        cbr = fig.colorbar(sm, cax=cax)
        cbr.outline.set_linewidth(0)
        tick_locator = ticker.MaxNLocator(nbins=nbins)
        cbr.locator = tick_locator
        cbr.update_ticks()
        cbr.ax.yaxis.set_tick_params(width=0.5)
        cbr.ax.tick_params(labelsize=6)  # Formatting for Colorbar Text
        for l in cbr.ax.yaxis.get_ticklabels():
            l.set_family("Libre Franklin")
        
        if unit is not None:
            if 0 < upper < 10:
                ax.text(0.823, 0.32, unit, transform=ax.transAxes, wrap = True, fontsize=6, fontname = 'Libre Franklin', verticalalignment='bottom', ha = 'left') 
            elif 10 <= upper < 100:
                ax.text(0.833, 0.32, unit, transform=ax.transAxes, wrap = True, fontsize=6, fontname = 'Libre Franklin', verticalalignment='bottom', ha = 'left')
            elif 100 <= upper < 1000:
                ax.text(0.845, 0.32, unit, transform=ax.transAxes, wrap = True, fontsize=6, fontname = 'Libre Franklin', verticalalignment='bottom', ha = 'left')
            elif 1000 <= upper < 100000:
                ax.text(0.856, 0.32, unit, transform=ax.transAxes, wrap = True, fontsize=6, fontname = 'Libre Franklin', verticalalignment='bottom', ha = 'left')
            else:
                pass
            
        
        return fig, ax
    
    def line_chart(data, ylab, xlab, **kwargs):
        
        ymax = kwargs.get('ymax', int(data.max()))
        ymin = kwargs.get('ymin', 0)
        
        delta = (ymax - ymin)/4
        i = 0
        while True:
            delta /= 10
            i += 1
            if delta < 10:
                break
        yinc = kwargs.get('yinc', int(round(delta+1)*pow(10,i)))
        
        fig, ax =plt.subplots()
        ax.plot(data ,linewidth=3, color = colour.purple)
        
        plt.grid()
        ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))

        ax.set_facecolor('xkcd:white')

        plt.xlabel(xlab, fontsize=9, fontweight = 'bold', horizontalalignment='right', x=0, labelpad=10, 
                   fontname = 'Libre Franklin')
        ax.grid(color='k', linestyle='-', linewidth=0.2)
        plt.ylabel(ylab, fontsize=9, fontweight = 'bold', horizontalalignment='right', y=1.0, 
                   labelpad=10, fontname = 'Libre Franklin')
        fig.set_size_inches(6.1, 4.1)
        month_lst2 = ['Sept\n2016',  'Jan\n2017',  'May',  'Sept',
                       'Jan\n2018', 'May',  'Sept', 
                      'Jan\n2019','May',]
        plt.xticks(fontsize=9, fontname = 'Libre Franklin')
        plt.yticks(range(ymin,int(4.1*yinc), yinc), fontsize =9, fontname = 'Libre Franklin')

        props = dict(boxstyle='round, pad=0.4',edgecolor=colour.purple, linewidth = 2, facecolor = 'w', alpha=1)


        ax.set_ylim([ymin,int(4*yinc+ymin)])
        fig.patch.set_facecolor('w')
        
        return fig, ax
    
    def tow_chart(data, ylab, **kwargs):
        
        ymax = kwargs.get('ymax', int(data.max()))
        ymin = kwargs.get('ymin', 0)
        
        delta = (ymax - ymin)/3
        i = 0
        while True:
            delta /= 10
            i += 1
            if delta < 10:
                break
        yinc = kwargs.get('yinc', int(round(delta+1)*pow(10,i)))
        fig, ax =plt.subplots()
        ax.plot(data, linewidth = 2.5, color = colour.purple)

        plt.grid()
        ax.set_facecolor('xkcd:white')

        plt.xlabel('Time of week', fontname = 'Libre Franklin', fontsize=9, horizontalalignment='left', x=0, labelpad=3, fontweight = 'bold')
        ax.set_ylim([ymin,int(3*yinc+ymin)])

        ax.grid(color='k', linestyle='-', linewidth=0.2)
        plt.ylabel(ylab, fontname = 'Libre Franklin', fontsize=9, horizontalalignment='right', y=1, labelpad=7, fontweight = 'bold')
        fig.set_size_inches(6.1, 1.8)


        ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
        plt.yticks(range(ymin,int(3.1*yinc), yinc), fontsize =9, fontname = 'Libre Franklin')

        ax.set_xticks(range(0,180,12))
        ax.set_xticklabels(['0','12','0','12',
                                                            '0','12','0','12',
                                         '0','12','0','12','0','12'], fontname = 'Libre Franklin', fontsize = 7, color = '#777777')

        ax.xaxis.set_minor_locator(ticker.FixedLocator(list(range(12,180,24))))
        ax.xaxis.set_minor_formatter(ticker.FixedFormatter(['Monday','Tuesday',
                                                            'Wednesday','Thursday',
                                         'Friday','Saturday','Sunday']))
        ax.tick_params(axis='x', which='minor', colors = 'k', labelsize=9, pad =14)

        props = dict(boxstyle='round, pad=0.3',edgecolor=colour.purple, linewidth = 1.5, facecolor = 'w', alpha=1)

        ax.set_xlim([0,167])
        plt.show()
        print(delta)
        return fig, ax

    def bar_chart():
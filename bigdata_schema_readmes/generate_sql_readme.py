import pandas
import os.path
from pathlib import Path
import configparser
from psycopg2 import connect

CONFIG = configparser.ConfigParser()
CONFIG.read(str(Path.home().joinpath('db.cfg'))) #Creates a path to your db.cfg file
dbset = CONFIG['DBSETTINGS']
con = connect(**dbset)

######################
##schema name goes here
######################
schema_name = 'miovision_api'
row_count_on = True #change to false to omit row counts (can be very slow on certain schemas)

#find table names from information_schema.tables
table_sql = '''
SELECT table_name 
FROM information_schema.tables
WHERE table_schema = '{}'
    AND table_type <> 'VIEW';
'''

#find column names and types from information_schema.columns
columns_sql = '''
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = '{}' 
    AND table_name = '{}';
'''

#first row of table as sample
sample_sql = '''
SELECT * 
FROM {}.{}
LIMIT 1;
'''

#first row of table as sample
rowcount_sql = '''
SELECT COUNT(1)
FROM {}.{};
'''

column_comments_sql = '''
    SELECT
        c.column_name,
        pgd.description
    FROM pg_catalog.pg_statio_all_tables AS st
    INNER JOIN pg_catalog.pg_description AS pgd ON (
        pgd.objoid = st.relid
    )
    INNER JOIN information_schema.columns AS c ON (
        pgd.objsubid = c.ordinal_position 
        AND c.table_schema = st.schemaname
        AND c.table_name = st.relname
    )
    WHERE c.table_schema = '{}' 
        AND c.table_name = '{}';
'''

#create directory if not exists 
#home folder
dir = "bigdata_schema_readmes"
if os.path.exists(dir) is False:
    os.mkdir(dir)
    print("Creating directory: {}".format(dir))

#remove file if exists
fname = dir + "/{}_readme.txt".format(schema_name)
if os.path.isfile(fname):
    os.remove(fname)

with con:
    #identify tables within schema
    tables = pandas.read_sql(table_sql.format(schema_name), con)
    
    if tables.empty:
        print("No tables found in schema '{}'".format(schema_name))

    #for each table
    for table_name in tables['table_name']:        

        #query columns & datatypes from information_schema
        column_types = pandas.read_sql(columns_sql.format(schema_name, table_name), con)

        #query sample row from schema.table and transpose 
        data_sample = pandas.read_sql(sample_sql.format(schema_name, table_name), con)       
        data_sample_T = data_sample.T
        data_sample_T["column_name"] = data_sample_T.index
        data_sample_T.rename(columns= {0: "sample"}, inplace=True)

        #row count 
        if row_count_on: 
            row_count = pandas.read_sql(rowcount_sql.format(schema_name, table_name), con)

        #column comments --tested with miovision_api (has 3 column comments)
        column_comments = pandas.read_sql(column_comments_sql.format(schema_name, table_name), con)
        
        #merge sample with column types
        final = column_types.merge(data_sample_T, how = 'left', on = 'column_name')
        final = final.merge(column_comments, how = 'left', on = 'column_name')
        final['description'] = final['description'].fillna('')

        #markdown format for github
        final_formatted = final.to_markdown(index = False)
        
        #print for debugging
        print(final_formatted)                   

        #write formatted output with table name as header        
        with open(fname, "a") as file: #append
            file.write("{}.{}\n".format(schema_name, table_name))
            if(row_count_on): 
                file.write("Row count: {:,}\n".format(row_count['count'][0]))
            file.write(final_formatted + "\n\n")
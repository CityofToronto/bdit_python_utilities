import pandas as pd
import os.path
import configparser
from psycopg2 import connect
from psycopg2 import sql

home_dir = os.path.expanduser('~')
    
CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(home_dir, 'db.cfg')) #Creates a path to your db.cfg file
dbset = CONFIG['DBSETTINGS']
con = connect(**dbset)

######################
##schema name goes here
######################
schema_name = input("Input schema name to generate schema readme for:") 
#schema_name = 'rescu'
row_count_on = input("Row count on? (True/False) Can be slow for certain schemas.")
#row_count_on = True #change to false to omit row counts (can be very slow on certain schemas)

#find table names from information_schema.tables
table_sql = sql.SQL('''
SELECT table_name 
FROM information_schema.tables
WHERE table_schema = {schema}
    AND table_type <> 'VIEW';
''')

#find column names and types from information_schema.columns
columns_sql = sql.SQL('''
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = {schema} 
    AND table_name = {table};
''')

#first row of table as sample
sample_sql = sql.SQL('''
SELECT * 
FROM {schema}.{table}
LIMIT 1;
''')

#first row of table as sample
rowcount_sql = sql.SQL('''
SELECT COUNT(1)
FROM {schema}.{table};
''')

column_comments_sql = sql.SQL('''
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
    WHERE c.table_schema = {schema} 
        AND c.table_name = {table};
''')

#create directory if not exists 
#home folder
dir = home_dir + "/bigdata_schema_readmes"
if os.path.exists(dir) is False:
    os.mkdir(dir)
    print("Creating directory: {}".format(dir))

#remove file if exists
fname = dir + "/{}_readme.txt".format(schema_name)
if os.path.isfile(fname):
    os.remove(fname)

print("Destination path: " + fname)
    
with con:
    
    #identify tables within schema
    tables = pd.read_sql_query(table_sql.format(
        schema = sql.Literal(schema_name)), con)

    if tables.empty:
        print(f"No tables found in schema '{schema_name}'")

    #for each table
    for table_name in tables['table_name']:        

        #query columns & datatypes from information_schema
        column_types = pd.read_sql(columns_sql.format(
            schema = sql.Literal(schema_name), 
            table = sql.Literal(table_name)), con)

        #query sample row from schema.table and transpose 
        data_sample = pd.read_sql(sample_sql.format(
            schema = sql.Identifier(schema_name),
            table = sql.Identifier(table_name)), con)       
        data_sample_T = data_sample.T
        data_sample_T["column_name"] = data_sample_T.index
        data_sample_T.rename(columns= {0: "sample"}, inplace=True)

        #row count 
        if row_count_on: 
            row_count = pd.read_sql(rowcount_sql.format(
                schema = sql.Identifier(schema_name),
                table = sql.Identifier(table_name)), con)

        #column comments --tested with miovision_api (has 3 column comments)
        column_comments = pd.read_sql(column_comments_sql.format(
            schema = sql.Literal(schema_name), 
            table = sql.Literal(table_name)), con)
        
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

print(f"File path of output: {fname}")
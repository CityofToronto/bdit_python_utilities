import pandas as pd
import os.path
import configparser
import sqlalchemy

home_dir = os.path.expanduser('~')

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(home_dir, 'db.cfg')) #Creates a path to your db.cfg file

"""
sqlalchemy cfg format:
[SQLALCHEMY]
host=
database=
username=
password=
"""
dbset = CONFIG['SQLALCHEMY']
url_object = sqlalchemy.engine.URL.create(
    "postgresql+psycopg2",
    **dbset
)
engine = sqlalchemy.create_engine(url_object)

######################
##schema name goes here
######################
schema_name = input("Input schema name to generate schema readme for:") 
#schema_name = 'ecocounter'
row_count_on = input("Row count on? (True/False) Can be slow for certain schemas.")
#row_count_on = True #change to false to omit row counts (can be very slow on certain schemas)

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

column_comments_sql = '''
SELECT
    a.attname AS column_name, 
    d.description AS "Comments"
FROM pg_class AS c
JOIN pg_attribute AS a ON c.oid = a.attrelid
JOIN pg_namespace AS n ON n.oid = c.relnamespace
JOIN pg_description AS d ON
    d.objoid = c.oid
    AND d.objsubid = a.attnum
WHERE
    n.nspname = '{}'
    AND c.relname = '{}'
    AND d.description IS NOT NULL;
'''

table_comments_sql = '''
SELECT pgd.description
FROM pg_description AS pgd
JOIN pg_class AS pgc ON pgd.objoid = pgc.oid
JOIN pg_namespace pgn ON pgc.relnamespace = pgn.oid
WHERE
    pgn.nspname = '{}'
    AND pgc.relname = '{}'
'''

#first row of table as sample
sample_sql = '''
SELECT * 
FROM {}.{}
LIMIT 1;
'''

#rowcount 
rowcount_sql = '''
SELECT COUNT(1)
FROM {}.{};
'''

#Don't fail if some columns are not in the dataset.
#Source: https://stackoverflow.com/a/62658311
def custom_dataset(dataset, req_cols):
    in_ = []
    if isinstance(dataset, pd.DataFrame):  # optional
        for col in req_cols:  # check for every existing column
            if col in dataset.columns:
                in_.append(col)  # append those that are in (i.e. valid)
    return dataset[in_] if in_ else None

#create directory if not exists 
dir = home_dir + "/bigdata_schema_readmes"
if os.path.exists(dir) is False:
    os.mkdir(dir)
    print("Creating directory: {}".format(dir))

#remove file if exists
fname = dir + "/{}_readme.txt".format(schema_name)
if os.path.isfile(fname):
    os.remove(fname)

with engine.connect() as con:
    #identify tables within schema
    tables = pd.read_sql(table_sql, con, params=(schema_name,))
    if tables.empty:
        print("No tables found in schema '{}'".format(schema_name))
    #for each table
    for table_name in tables['table_name']: 
        print(table_name)
        #query columns & datatypes from information_schema
        column_types = pd.read_sql(columns_sql, con, params=(schema_name, table_name))
        column_comments = pd.read_sql(column_comments_sql, con, params=(schema_name, table_name))
        #query sample row from schema.table and transpose 
        data_sample = pd.read_sql(sample_sql, con, params=(schema_name, table_name))
        data_sample_T = data_sample.T
        data_sample_T["column_name"] = data_sample_T.index
        data_sample_T.rename(columns= {0: "sample"}, inplace=True)        
        table_comments = pd.read_sql(table_comments_sql, con, params=(schema_name, table_name))
        try:
            table_comment = table_comments['description'][0]
        except KeyError:
            table_comment = ''
        #row count 
        if row_count_on: 
            row_count = pd.read_sql(rowcount_sql, con, params=(schema_name, table_name))
        #merge sample with column types, comments
        final = column_types.merge(data_sample_T, on = 'column_name')
        final = column_comments.merge(final, on = 'column_name', how='right')
        #reorder columns
        final=custom_dataset(final, ['Column Name', 'Data Type', 'Sample', 'Comments'])
        #replace nans
        final.fillna('', inplace=True)
        #markdown format for github
        final_formatted = final.to_markdown(index = False, tablefmt="github")        
        #print for debugging
        #print(final_formatted)        
        #write formatted output with table name as header        
        with open(fname, "a") as file: #append
            file.write("### `{}.{}`\n".format(schema_name, table_name))
            file.write(f"{table_comment}\n\n")
            if(row_count_on): 
                file.write("Row count: {:,}\n".format(row_count['count'][0]))
            file.write(final_formatted + "\n\n")

print(f"File path of output: {fname}")

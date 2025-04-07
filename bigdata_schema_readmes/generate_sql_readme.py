import pandas as pd
import os.path
import configparser
import sqlalchemy
from sqlalchemy import sql

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
input_schema = input("Input schema name to generate schema readme for:") 

# Parse schema and prefix from input
try:
    schema_name, table_prefix = input_schema.split('.')
except ValueError:
    schema_name = input_schema

#find table names from information_schema.tables
if table_prefix:
    table_sql = sql.text('''
    SELECT
        c.relname AS table_name,
        CASE c.relkind
            WHEN 'p' THEN 'partitioned table'
            WHEN 'r' THEN 'table'
        END AS table_type
    FROM pg_catalog.pg_class AS c
    JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
    WHERE
        n.nspname = :schema
        AND c.relname LIKE :prefix
        -- add more type: https://www.postgresql.org/docs/current/catalog-pg-class.html
        AND c.relkind = ANY('{p,r}')
    AND NOT c.relispartition --exclude child partitions
    ORDER BY 1, 2;
    ''')
else:
    table_sql = sql.text('''
    SELECT
        c.relname AS table_name,
        CASE c.relkind
            WHEN 'p' THEN 'partitioned table'
            WHEN 'r' THEN 'table'
        END AS table_type
    FROM pg_catalog.pg_class AS c
    JOIN pg_catalog.pg_namespace AS n ON n.oid = c.relnamespace
    WHERE
        n.nspname = :schema
        -- add more type: https://www.postgresql.org/docs/current/catalog-pg-class.html
        AND c.relkind = ANY('{p,r}')
    AND NOT c.relispartition --exclude child partitions
    ORDER BY 1, 2;
    ''')

#find column names and types from information_schema.columns
columns_sql = sql.text('''
SELECT
    a.attname AS "Column Name", 
    d.description AS "Comments",
    pg_catalog.format_type(a.atttypid, a.atttypmod) as "Data Type"
FROM pg_class AS c
JOIN pg_attribute AS a ON c.oid = a.attrelid
JOIN pg_namespace AS n ON n.oid = c.relnamespace
LEFT JOIN pg_description AS d ON
    d.objoid = c.oid
    AND d.objsubid = a.attnum
WHERE
    n.nspname = :schema
    AND c.relname = :table
    AND attisdropped = false
    AND attnum >= 1;
''')

table_comments_sql = sql.text('''
SELECT pgd.description
FROM pg_description AS pgd
JOIN pg_class AS pgc ON pgd.objoid = pgc.oid
JOIN pg_namespace pgn ON pgc.relnamespace = pgn.oid
WHERE
    pgn.nspname = :schema
    AND pgc.relname = :table
''')

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
    if table_prefix:
        tables = pd.read_sql_query(table_sql, con, params={'schema': schema_name, 'prefix': f"{table_prefix}%"})
    else:
        tables = pd.read_sql_query(table_sql, con, params={'schema': schema_name})
    if tables.empty:
        print("No tables found in schema '{}'".format(schema_name))
    #for each table
    for table_name in tables['table_name']: 
        print(f"Processing {table_name}...")
        #query columns & datatypes from information_schema
        column_types = pd.read_sql_query(columns_sql, con, params={'schema': schema_name, 'table': table_name})
        #query sample row from schema.table and transpose
        sample_query = sql.text(f"SELECT * FROM {schema_name}.{table_name} LIMIT 1")
        data_sample = pd.read_sql_query(sample_query, con)
        data_sample_T = data_sample.T
        data_sample_T["Column Name"] = data_sample_T.index
        data_sample_T.rename(columns= {0: "Sample"}, inplace=True)
        table_comments = pd.read_sql_query(table_comments_sql, con, params={'schema': schema_name, 'table': table_name})
        try:
            table_comment = table_comments['description'][0]
        except KeyError:
            table_comment = ''
        #approx row count
        rowcount_sql = sql.text(f'''
        SELECT TO_CHAR(COUNT(1) * 100, '999,999,999,999,999') AS c FROM {schema_name}.{table_name} TABLESAMPLE SYSTEM (1);
        ''')
        row_count = pd.read_sql_query(rowcount_sql, con)
        #merge sample with column types, comments
        final = column_types.merge(data_sample_T, on = 'Column Name')
        #reorder columns
        final=custom_dataset(final, ['Column Name', 'Data Type', 'Sample', 'Comments'])
        #replace nans
        final.fillna('', inplace=True)
        #markdown format for github
        final_formatted = final.to_markdown(index = False, tablefmt="github")        
        object_type = tables.loc[tables.table_name == table_name, 'table_type'].iloc[0]
        
        #write formatted output with table name as header
        with open(fname, "a") as file: #append
            file.write(f"### `{schema_name}.{table_name}` ({object_type})\n")
            file.write(f"{table_comment}\n")
            file.write(f"Approx row count: {row_count['c'][0]}\n")
            file.write(final_formatted + "\n\n")

print(f"File path of output: {fname}")
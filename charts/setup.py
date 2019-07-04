from setuptools import setup, find_packages

setup(
    name='vfh_charts',
    version='0.1',
    description='Standardized matplotlib charts and graphs',
    packages=find_packages(),
    install_requires=[
        'matplotlib',
        'psycopg2',
        'geopandas',
        'pandas',
        'shapely'
    ],
    python_requires='>=3'
)
from setuptools import setup, find_packages

setup(
    name='email_notifications',
    version='0.1',
    description='Simplified email module for sending plaintext emails through gmail',
    packages=find_packages(),
    install_requires=[
        'httplib2',
        'google-api-python-client',
        'oauth2client'
    ],
    python_requires='>=3'
)
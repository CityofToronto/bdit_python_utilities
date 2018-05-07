from setuptools import setup

setup(
    name='email_notifications',
    version='0.1',
    description='Simplified email module for sending plaintext emails through gmail'
    py_modules=['notify_email'],
    install_requires=[
        'httplib2',
        'google-api-python-client',
        'oauth2client'
    ],
    python_requires='>=3'
)
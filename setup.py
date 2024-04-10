from setuptools import setup

setup(
    name='Py-Wormgrok',
    version='0.0.0',
    packages=['wormgrok'],
    install_requires=[
        'aiohttp~=3.9',
        'ngrok~=1.2'
    ],
    author='deadbeef-development',
    author_email='deadbeef.development@gmail.com'
)
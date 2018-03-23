from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mqttwrapper',
    version='0.0.4',
    description='MQTT utility scripts made easy',
    long_description=long_description,
    url='https://github.com/davea/mqttwrapper',
    license='MIT',
    author='Dave Arter',
    author_email='pypi@davea.me',
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='mqtt',
    packages=find_packages(),
    install_requires=['paho-mqtt'],
    extras_require={
        'hbmqtt': ['hbmqtt'],
    },
)
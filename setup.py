#!/usr/bin/env python

from setuptools import setup

with open("README.md") as readme:
    long_description = readme.read()

with open("requirements.txt") as f:
    install_requires = f.read().split()

setup(
    name='pyseeder',
    version='0.0.1',
    description='Python reseed utilities for I2P',
    long_description=long_description,
    author='Darnet Villain',
    author_email='supervillain@riseup.net',
    url='https://github.com/PurpleI2P/pyseeder/',
    keywords='i2p reseed',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=['pyseeder', 'pyseeder.transports'],
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'pyseeder=pyseeder.cli:main',
        ],
    }
)

from setuptools import find_packages, setup

setup(
    name='mediastrends',
    entry_points = {
        'console_scripts': ['mediastrends=mediastrends.cli:main']
    },
    packages=find_packages(),
    version='0.1.0',
    description='Trends of medias',
    author='prise6',
    license='Prise6 Copyright 2020',
)
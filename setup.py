from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()
    requirements.pop()

setup(
    name='mediastrends',
    version='1.0.0',
    entry_points={
        'console_scripts': ['mediastrends=mediastrends.cli:main']
    },
    packages=find_packages(),
    include_package_data=True,
    platforms=['any'],
    install_requires=requirements,
    url="https://github.com/prise6/medias-trends",
    description='Trends of medias torrents',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='prise6',
    author_email="vieille.francois@gmail.com",
    license='NeedToBeDetermined',
    python_requires='>=3.6'
)

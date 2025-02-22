from setuptools import setup, find_packages

from os import path
here = path.abspath(path.dirname(__file__))

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Intended Audience :: Customer Service',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Telecommunications Industry',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3'
]

setup(
    name='searoute',
    version='1.4.3',
    description='A python package for generating the shortest sea route between two points on Earth.',
    long_description=open('README.md').read() + '\n\n' +
    open('CHANGELOG.txt').read(),
    long_description_content_type="text/markdown",
    url='',
    author='Gent Halili',
    author_email='genthalili@users.noreply.github.com',
    license='Apache License 2.0',
    classifiers=classifiers,
    keywords='searoute map sea route ocean ports',
    packages=find_packages(),
    install_requires=['geojson', 'networkx'],
    project_urls={
        "Documentation": "https://github.com/genthalili/searoute-py/blob/main/README.md",
        "Source": "https://github.com/genthalili/searoute-py",
    },
    include_package_data=True,
)

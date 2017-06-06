import os

from setuptools import setup, find_packages


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()

setup(
    name='app',
    version='0.1',
    author='Nicolas Maurice',
    autho_email='nicolas.maurice@fr.ey.com',
    description=('Partially decentralized app that listens to Vertogas Smart Contract on Ethereum Blockchain and '
                 'handles convenient information replication in a SQL database'),
    license='BSD',
    packages=find_packages(exclude='tests'),
    long_description=read('README.md'),
    include_package_data=True,
    install_requires=[
        'certifi==2017.4.17',
        'chardet==3.0.3',
        'click==6.7',
        'ethereum-abi-utils==0.4.0',
        'ethereum-utils==0.2.0',
        'idna==2.5',
        'marshmallow==2.13.5',
        'prettytable==0.7.2',
        'psycopg2==2.7.1',
        'pylru==1.0.9',
        'pysha3==1.0.2',
        'requests==2.17.3',
        'rlp==0.5.1',
        'SQLAlchemy==1.1.10',
        'urllib3==1.21.1',
        'web3==3.8.1',
    ],
    extra_requires={
        'develop': [
            'coverage',
            'pytest>3',
            'pytest-cov',
            'tox',
        ]
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points='''
        [console_scripts]
        vertogas=app.cli:cli
    ''',
)

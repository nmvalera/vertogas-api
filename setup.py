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
    extras_require={
        'dev': [
            'coverage',
            'pytest>3',
            'pytest-cov',
            'pytest-flask==0.10.0',
            'tox',
        ]
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points='''
        [console_scripts]
        vertogas=app.cli:cli
    ''',
)

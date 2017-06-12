import click

from .tokens.cli import cli as vertogas_cli
from .web3.cli import cli as web3_cli


@click.group()
def cli():
    pass

cli = click.CommandCollection(sources=[cli, vertogas_cli, web3_cli])

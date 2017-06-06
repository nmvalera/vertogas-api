import click

from .tokens.cli import cli as vertogas_cli
from .web3.cli import cli as web3_cli

cli = click.CommandCollection(sources=[vertogas_cli, web3_cli])

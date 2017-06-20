import click

from .common import FROM_BLOCK_KEY, TO_BLOCK_KEY
from .tasks import update_contracts_chain
from .tokens.cli import cli as vertogas_cli
from .web3.cli import cli as web3_cli


@click.group()
def cli():
    pass


@cli.command('update_logs')
@click.option('--contracts', '-c',
              multiple=True,
              help='IDs of the contracts')
def update_logs(contracts):
    logs_tokens = update_contracts_chain(contracts)()
    for logs_token in logs_tokens:
        logs = logs_token['logs']
        from_block, to_block = logs['filter_param'][FROM_BLOCK_KEY], logs['filter_param'][TO_BLOCK_KEY]
        msg = "Correctly updated logs of contract %s from block %s to block %s (total %s blocks)" % \
              (logs['contract']['id'], from_block, to_block, to_block - from_block + 1)
        click.echo(click.style(msg,
                               fg='green',
                               bold=True))

cli = click.CommandCollection(sources=[cli, vertogas_cli, web3_cli])

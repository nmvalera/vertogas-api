import json

import click
from prettytable import PrettyTable

from .helpers import TokenHelpers
from ..common.constants import TOKEN_ID_KEY


@click.group()
def cli():
    pass


@cli.command('init_db')
@click.option('--uri',
              help='URI of the database (e.g. postgresql://postgres:postgres@localhost:5432/postgres)')
def init_db(uri):
    """
    Initialize the database 
    """
    token_helpers = TokenHelpers(uri)
    tables = token_helpers.init_db()
    token_helpers.commit()
    output_msg = "Vertogas database has been correctly initialized with %s tables:" % len(tables)
    click.echo(click.style(output_msg, fg='green', bold=True))
    for table_name in tables:
        click.echo(click.style("- %s" % table_name, fg='green'))


@cli.command('insert_contract')
@click.option('--address',
              help='Contract address in the Blockchain')
@click.option('--abi',
              help='Path of the file containing the contract abi')
@click.option('--uri',
              help='URI of the database (e.g. postgresql://postgres:postgres@localhost:5432/postgres)')
def insert_contract(address, abi, uri):
    """
    Insert a contract in the database 
    """
    token_helpers = TokenHelpers(uri)
    with open(abi, 'rb') as json_abi:
        abi = json_abi.read()
        contract = token_helpers.insert_contract(address, abi)
        token_helpers.commit()
    click.echo(click.style("Contract correctly inserted [id=%s]:" % contract.id, fg='green', bold=True))
    click.echo(click.style("- Address: %s" % address, fg='green'))
    click.echo(click.style("- ABI: %s" % abi.decode(), fg='green'))


@cli.command('contracts')
@click.option('--uri',
              help='URI of the database (e.g. postgresql://postgres:postgres@localhost:5432/postgres)')
def contracts(uri):
    """
    List all contracts
    """
    tab = PrettyTable()
    helpers = TokenHelpers(uri)
    tab._set_field_names(['Address', 'ID', 'Is listening', 'Last block'])
    for contract in helpers.get_contracts():
        tab.add_row([contract.address, contract.id, contract.is_listening, contract.last_block])
    click.echo(tab.get_string())


@cli.command('events')
@click.option('--contract',
              help='ID of the contracts')
@click.option('--uri',
              help='URI of the database (e.g. postgresql://postgres:postgres@localhost:5432/postgres)')
def events(contract, uri):
    """
    List all events for a given contract
    """
    tab = PrettyTable()
    token_helpers = TokenHelpers(uri)
    contract = token_helpers.get_contract(contract)
    click.echo(click.style("Contract [id=%s] at address %s" % (contract.id, contract.address), bold=True))
    tab._set_field_names(['Event Name', 'Log count'])
    for event in contract.events:
        tab.add_row([event.name, event.logs.count()])
    click.echo(tab.get_string())


@cli.command('logs')
@click.option('--contract',
              help='ID of the contracts')
@click.option('--uri',
              help='URI of the database (e.g. postgresql://postgres:postgres@localhost:5432/postgres)')
def logs(contract, uri):
    """
    List all logs for a given contract
    """
    tab = PrettyTable()
    token_helpers = TokenHelpers(uri)
    contract = token_helpers.get_contract(contract)
    click.echo(click.style("Contract [id=%s] at address %s" % (contract.id, contract.address), bold=True))
    tab._set_field_names(['Event Name', 'Token ID', 'Certificate ID', 'Block Number', 'Block Timestamp'])
    for log in token_helpers.get_logs(contract.id):
        tab.add_row([log.event.name, log.token_id, log.token.certificate_id, log.block_number, log.timestamp])
    click.echo(tab.get_string())


@cli.command('tokens')
@click.option('--contract',
              help='ID of the contracts')
@click.option('--uri',
              help='URI of the database (e.g. postgresql://postgres:postgres@localhost:5432/postgres)')
def tokens(contract, uri):
    """
    List all tokens for a given contract
    """
    tab = PrettyTable()
    token_helpers = TokenHelpers(uri)
    contract = token_helpers.get_contract(contract)
    click.echo(click.style("Contract [id=%s] at address %s" % (contract.id, contract.address), bold=True))
    tab._set_field_names(['Token ID', 'Owner', 'Claimed'])
    for token in token_helpers.get_tokens(contract.id):
        tab.add_row([token.id, token.owner, token.is_claimed])
    click.echo(tab.get_string())

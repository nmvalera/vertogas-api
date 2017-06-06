import json

from ..common.constants import FROM_BLOCK_KEY, TO_BLOCK_KEY, BLOCK_NUMBER_KEY


def get_current_block_number(web3):
    """
    Get the current block number 
    :param web3: web3 instance to perform jsonRPC calls
    :return: number of the current block
    """
    return web3.eth.blockNumber


def get_block(block_number, web3):
    """
    Request information on a block
    :param block_number: block number
    :param web3: web3 instance to perform jsonRPC calls
    :return: block information in jsonRPC format
    """
    return web3.eth.getBlock(block_number)


def make_web3_event_filters(contract, from_block, to_block, web3):
    """
    Set event filters for a given contract 
    :param contract: SQLAlchemy contract object
    :param from_block: filter range lower bound
    :param to_block: filter range upper bound
    :param web3: web3 instance to perform jsonRPC calls
    :return: list of event filters
    """
    web3_contract = web3.eth.contract(contract.address, abi=json.loads(contract.abi))
    filter_param = {
        FROM_BLOCK_KEY: from_block or contract.last_block + 1,
        TO_BLOCK_KEY: to_block or 'latest',
    }
    event_filters = []
    for event in contract.events:
        event_filters.append({
            'id': event.id,
            'filter': web3_contract.on(event.name, filter_param),
        })
    return event_filters


def get_logs(contract, from_block, to_block, web3):
    """
    Given a list of event filters, request all the logs
    :param contract: SQLAlchemy contract object
    :param from_block: filter range lower bound
    :param to_block: filter range upper bound
    :param web3: web3 instance to perform jsonRPC calls
    :return: list of logs
    """
    event_filters = make_web3_event_filters(contract, from_block, to_block, web3)
    logs = [{'id': event_filter['id'], 'log': log}
            for event_filter in event_filters
            for log in event_filter['filter'].get(only_changes=False)]
    return sorted(logs, key=lambda log: log['log'][BLOCK_NUMBER_KEY])

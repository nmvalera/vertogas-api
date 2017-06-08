import json

from .web3 import default_web3
from ..common.config import config
from ..common.constants import FROM_BLOCK_KEY, TO_BLOCK_KEY, BLOCK_NUMBER_KEY
from ..tokens.helpers import TokenHelpers


class Web3Helpers:
    def __init__(self, web3=default_web3):
        self.web3 = web3

    def get_current_block_number(self):
        """
        Get the current block number 
        :param web3: web3 instance to perform jsonRPC calls
        :return: number of the current block
        """
        return self.web3.eth.blockNumber

    def get_block(self, block_number):
        """
        Request information on a block
        :param block_number: block number
        :param web3: web3 instance to perform jsonRPC calls
        :return: block information in jsonRPC format
        """
        return self.web3.eth.getBlock(block_number)

    def make_web3_event_filters(self, contract, from_block, to_block):
        """
        Set event filters for a given contract 
        :param contract: SQLAlchemy contract object
        :param from_block: filter range lower bound
        :param to_block: filter range upper bound
        :param web3: web3 instance to perform jsonRPC calls
        :return: list of event filters
        """
        web3_contract = self.web3.eth.contract(contract.address, abi=json.loads(contract.abi))
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

    def get_logs(self, contract, from_block, to_block):
        """
        Given a list of event filters, request all the logs
        :param contract: SQLAlchemy contract object
        :param from_block: filter range lower bound
        :param to_block: filter range upper bound
        :param web3: web3 instance to perform jsonRPC calls
        :return: list of logs
        """
        event_filters = self.make_web3_event_filters(contract, from_block, to_block)
        logs = [{'id': event_filter['id'], 'log': log}
                for event_filter in event_filters
                for log in event_filter['filter'].get(only_changes=False)]
        return sorted(logs, key=lambda log: log['log'][BLOCK_NUMBER_KEY])

    def update_logs(self, contract_id=None, to_block=None, uri=None):
        """
        Update the logs for a contract
        :param contract_id: id of the contract to update (if None then choose the less updated contract)
        :param to_block: block number
        :param uri: uri of the database (default: uses the uri of the database 
        """
        token_helpers = TokenHelpers(uri)
        if contract_id:
            contract = token_helpers.get_contract(contract_id)
        else:
            contract = token_helpers.get_less_updated_contract()

        # Computes logs for the range of blocks to inspect
        current_block = self.get_current_block_number()
        to_block = min(to_block, current_block) if to_block else current_block - config.SAFETY_BLOCK_COUNT
        from_block = min(contract.last_block + 1, to_block)
        logs = self.get_logs(contract, from_block, to_block)

        # Perform database insertions
        for log in logs:
            block = self.get_block(log['log'][BLOCK_NUMBER_KEY])  # block timestamp is useful
            token_helpers.insert_log(log['id'], block, log['log'])
        token_helpers.set_last_block(contract, to_block)
        token_helpers.commit()

        return contract, from_block, to_block

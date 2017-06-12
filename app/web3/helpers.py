import json

from .utils import make_filter_param, expand_logs
from .web3 import default_web3
from ..common.config import config
from ..common.constants import BLOCK_NUMBER_KEY


class Web3Helpers:
    def __init__(self, web3=default_web3):
        self.web3 = web3

    def get_current_block_number(self):
        """
        Get the current block number 
        :return: number of the current block
        """
        return self.web3.eth.blockNumber

    def get_block(self, block_number):
        """
        Request information on a block
        :param block_number: block number
        :return: block information in jsonRPC format
        """
        return self.web3.eth.getBlock(block_number)

    def make_web3_contract(self, address, abi):
        return self.web3.eth.contract(address, abi=abi)

    def enrich_log(self, log):
        return {**log, 'block': self.get_block(log[BLOCK_NUMBER_KEY])}

    def get_event_logs(self, contract, event, filter_param):
        web3_contract = self.make_web3_contract(contract['address'], abi=json.loads(contract['abi']))
        return {
            'event_id': event['id'],
            'logs': [
                self.enrich_log(log) for log in web3_contract.on(event['name'], filter_param).get(only_changes=False)
            ]
        }

    def get_logs(self, contracts, from_block=None, to_block=None):
        if isinstance(contracts, list):
            return [self.get_logs(contract, from_block, to_block) for contract in contracts]

        else:
            # ensure from_block and to_block are consistent
            current_block = self.get_current_block_number()
            safe_block = current_block - config.SAFETY_BLOCK_COUNT
            to_block = min(to_block or safe_block, current_block)
            from_block = from_block or contracts['last_block'] + 1
            filter_param = make_filter_param(contracts, from_block, to_block)
            logs = expand_logs([self.get_event_logs(contracts, event, filter_param) for event in contracts['events']])
            return {
                'data': logs,
                'filter_param': filter_param,
                'contract': contracts,
            }

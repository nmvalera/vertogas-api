import json

from .web3 import default_web3


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
        return self.web3.eth.contract(address, abi=json.loads(abi))

    def get_event_log(self, contract, event, filter_param):
        web3_contract = self.make_web3_contract(contract['address'], abi=json.loads(contract['abi']))
        return  {
            'event_id': event['id'],
            'logs': web3_contract.on(event['name'], filter_param).get(only_changes=False)
        }

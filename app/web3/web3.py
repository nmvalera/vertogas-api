from web3 import Web3, KeepAliveRPCProvider
from ..common.config import config

def create_web3(parity_server_host=config.PARITY_SERVER_HOST, parity_server_port=config.PARITY_SERVER_PORT):
    provider = KeepAliveRPCProvider(host=parity_server_host, port=parity_server_port)
    return Web3(provider)

default_web3 = create_web3()

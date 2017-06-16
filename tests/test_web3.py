import json
from app.tokens.helpers import TokenHelpers
from app.web3.helpers import Web3Helpers
from .testconf import BLOCK_NUMBER, BLOCK, \
    CONTRACT_ADDRESS, CONTRACT_ABI

def setup_module(module):
    """Setup database for testing"""
    token_helpers = TokenHelpers()
    token_helpers.init_db()
    token_helpers.commit()


def teardown_module(module):
    """Tear down database"""
    token_helpers = TokenHelpers()
    token_helpers.drop_db()
    token_helpers.commit()
    token_helpers.close()


def test_get_current_block():
    web3_helpers = Web3Helpers()
    current_block = web3_helpers.get_current_block_number()
    assert current_block > 0


def test_get_block():
    web3_helpers = Web3Helpers()
    block = web3_helpers.get_block(BLOCK_NUMBER)
    print(block)
    assert block == BLOCK


def test_get_logs():
    web3_helpers = Web3Helpers()
    web3_contract = web3_helpers.make_web3_contract(CONTRACT_ADDRESS, json.loads(CONTRACT_ABI.decode()))
    assert web3_contract is not None



if __name__ == "__main__":
    block = Web3Helpers().get_block(1264783)
    print(block)
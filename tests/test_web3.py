import json

from app.tokens.helpers import TokenHelpers
from app.tokens.serializers import contract_schema
from app.web3.helpers import Web3Helpers
from .constants import BLOCK_NUMBER, BLOCK, \
    CONTRACT_ADDRESS, CONTRACT_ABI
from app.common import  FROM_BLOCK_KEY, TO_BLOCK_KEY

def setup_module(module):
    """Setup database for testing"""
    token_helpers = TokenHelpers()
    token_helpers.init_db()
    token_helpers.insert_contract(CONTRACT_ADDRESS, CONTRACT_ABI)
    token_helpers.insert_data(
        ['data/power_plants.pickle', 'data/biomass.pickle', 'data/mixes.pickle'],
        ['power_plants', 'biomass', 'mixes']
    )
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
    assert block == BLOCK


def test_make_web3_contract():
    web3_helpers = Web3Helpers()
    web3_contract = web3_helpers.make_web3_contract(CONTRACT_ADDRESS, json.loads(CONTRACT_ABI.decode()))
    assert web3_contract


def _test_get_logs(contracts, from_block, to_block):
    web3_helpers = Web3Helpers()
    logs = web3_helpers.get_logs(contracts, from_block, to_block)
    assert isinstance(logs, list)
    assert len(logs) == len(contracts)

    return logs


def _test_log_batch(log_batch, contract, expected_log_count):
    assert 'data' in log_batch
    data = log_batch['data']
    assert 'filter_param' in log_batch
    filter_param = log_batch['filter_param']
    assert 'contract' in log_batch
    assert log_batch['contract'] == contract
    assert len(data) == expected_log_count

    return data, filter_param


def test_get_logs():
    token_helpers = TokenHelpers()
    contracts = contract_schema.dump(token_helpers.get_contracts([1]), many=True).data
    token_helpers.close()

    for from_block, to_block, expected_log_count in zip(
            [0, 16893, 1892, 1784, 0, 1802481, 1802556, 0, 0],
            [10, 163534, 1287642, 1784, 1802490, 1802522, 1802556, 1915068, 2042415],
            [0, 0, 0, 0, 1, 3, 1, 11, 12]):
        for log_batch, contract in zip(_test_get_logs(contracts, from_block, to_block), contracts):
            data, filter_param = _test_log_batch(log_batch, contract, expected_log_count)
            assert filter_param[FROM_BLOCK_KEY] == from_block
            assert filter_param[TO_BLOCK_KEY] == to_block

def test_insert_logs():
    token_helpers = TokenHelpers()
    web3_helpers = Web3Helpers()
    contract_id= 1
    contracts = contract_schema.dump(token_helpers.get_contracts([contract_id]), many=True).data

    token_helpers.insert_logs(web3_helpers.get_logs(contracts, 0, 1802490))
    token_helpers.commit()
    assert len(token_helpers.get_logs(contract_id)) == 1
    assert len(token_helpers.get_tokens(contract_id)) == 1

    token_helpers.insert_logs(web3_helpers.get_logs(contracts, 1802491, 1802556))
    token_helpers.commit()
    assert len(token_helpers.get_logs(contract_id)) == 6
    assert len(token_helpers.get_tokens(contract_id)) == 2

    token_helpers.insert_logs(web3_helpers.get_logs(contracts, 1802557, 2042415))
    token_helpers.commit()
    assert len(token_helpers.get_logs(contract_id)) == 12
    assert len(token_helpers.get_tokens(contract_id)) == 7
    token_helpers.close()

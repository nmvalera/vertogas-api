import pytest

from app.web3.tasks import update_logs
from app.tokens.helpers import TokenHelpers
from .testconf import CONTRACT_ADDRESS, CONTRACT_ABI

"""
def initialize_db():
    token_helpers = TokenHelpers()
    token_helpers.init_db()
    token_helpers.insert_contract(CONTRACT_ADDRESS, CONTRACT_ABI)
    token_helpers.commit()
    print("database initialized")


def test_update_logs():
    initialize_db()
    contract_id = 1
    update_logs(contract_id, 10)
    token_helpers = TokenHelpers()
    contract = token_helpers.get_contract(contract_id)
    assert contract.tokens.count() == 0
    assert contract.last_block == 10
"""





from .utils import get_current_block_number, get_logs, get_block
from .web3 import default_web3
from ..common.config import config
from ..common.constants import BLOCK_NUMBER_KEY
from ..tokens.helpers import TokenHelpers


def update_logs(contract=None, to_block=None, uri=None, web3=default_web3):
    """
    Update the logs for the contract that has been the least updated
    """
    token_helpers = TokenHelpers(uri)
    if contract:
        contract = token_helpers.get_contract(contract)
    else:
        contract = token_helpers.get_less_updated_contract()

    # Computes logs for the range of blocks to inspect
    to_block = to_block or get_current_block_number(web3) - config.SAFETY_BLOCK_COUNT
    from_block = min(contract.last_block + 1, to_block)
    logs = get_logs(contract, from_block, to_block, web3)

    # Perform database insertions
    for log in logs:
        block = get_block(log['log'][BLOCK_NUMBER_KEY], web3)  # get block information (timestamp is specially useful)
        token_helpers.insert_log(log['id'], block, log['log'])
    token_helpers.set_last_block(contract, to_block)
    token_helpers.commit()

    return contract, from_block, to_block

from celery import signature, chord

from .celery import app
from .tokens.constants import TASK_GET_CONTRACT, TASK_INSERT_LOGS
from .web3.constants import TASK_GET_ENRICHED_LOGS
from .common.constants import TASK_UPDATE_LOGS


@app.task(name=TASK_UPDATE_LOGS)
def update_logs(contract_id=None, from_block=None, to_block=None):
    chain = signature(TASK_GET_CONTRACT, args=(contract_id,))
    chain |= signature(TASK_GET_ENRICHED_LOGS, args=(from_block, to_block))
    chain |= signature(TASK_INSERT_LOGS, args=())
    return chain()


@app.task(name=TASK_UPDATE_ALL_CONTRACTS)
def update_all_contracts(contract_ids):
    chain = chord(update_logs.s(contract_id) for contract_id in contract_ids)
    return chain()


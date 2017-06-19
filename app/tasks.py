from celery import signature

from .celery import app
from .common.constants import TASK_UPDATE_LISTENING_CONTRACTS
from .tokens.constants import TASK_INSERT_LOGS, TASK_GET_CONTRACTS
from .web3.constants import TASK_GET_LOGS


def update_contracts_chain(contract_ids=None, only_listening=True):
    chain = signature(TASK_GET_CONTRACTS, args=(contract_ids, only_listening)) | \
            signature(TASK_GET_LOGS, args=()) | \
            signature(TASK_INSERT_LOGS, args=())
    return chain


@app.task(name=TASK_UPDATE_LISTENING_CONTRACTS)
def update_listening_contracts():
    update_contracts_chain().apply_async()

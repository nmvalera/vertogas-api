from celery import signature

from .celery import app
from .common.constants import TASK_UPDATE_LISTENING_CONTRACTS
from .tokens.constants import TASK_INSERT_LOGS, TASK_GET_CONTRACTS
from .web3.constants import TASK_GET_LOGS


@app.task(name=TASK_UPDATE_LISTENING_CONTRACTS)
def update_listening_contracts():
    chain = signature(TASK_GET_CONTRACTS, args=()) | \
            signature(TASK_GET_LOGS, args=()) | \
            signature(TASK_INSERT_LOGS, args=())
    chain.apply_async()

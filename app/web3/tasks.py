from celery import Task

from .constants import TASK_GET_LOGS, TASK_GET_CURRENT_BLOCK_NUMBER
from .helpers import Web3Helpers
from ..celery import app


class Web3Task(Task):
    abstract = True

    def __init__(self):
        super().__init__()
        self.web3_helpers = Web3Helpers()


@app.task(name=TASK_GET_LOGS,
          base=Web3Task,
          autoretry_for=(Exception,),
          default_retry_delay=1,
          max_retries=5,
          bind=True)
def get_logs(self, contracts, from_block=None, to_block=None):
    """
    
    :param self: task
    :param contracts: list of form [contracts, current_block_number]
    :return: 
    """
    return self.web3_helpers.get_logs(contracts, from_block, to_block)


@app.task(name=TASK_GET_CURRENT_BLOCK_NUMBER,
          base=Web3Task,
          autoretry_for=(Exception,),
          default_retry_delay=1,
          max_retries=5,
          bind=True)
def get_current_block_number(self):
    return self.web3_helpers.get_current_block_number()

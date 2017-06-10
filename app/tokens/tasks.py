from celery import Task

from .constants import TASK_INSERT_LOGS, TASK_GET_CONTRACT
from .helpers import TokenHelpers
from .serializers import token_schema, contract_schema
from ..celery import app


class TokenTask(Task):
    abstract = True

    def __init__(self, session=None):
        super().__init__()
        self.token_helpers = TokenHelpers(session)


@app.task(name=TASK_GET_CONTRACT, base=TokenTask, bind=True)
def get_contract(self, contract_id=None):
    if contract_id:
        contract = self.token_helpers.get_contract(contract_id)
    else:
        contract = self.token_helpers.get_less_updated_contract()
    return contract_schema.dump(contract).data


@app.task(name=TASK_INSERT_LOGS, base=TokenTask, bind=True)
def insert_logs(self, contract_id, logs, from_block, to_block):
    tokens = self.token_helpers.insert_logs(contract_id, logs, to_block)
    self.token_helpers.commit()
    return contract_id, token_schema.dump(tokens).data, from_block, to_block

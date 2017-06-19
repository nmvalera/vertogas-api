from celery import Task

from .constants import TASK_INSERT_LOGS, TASK_GET_CONTRACT, TASK_GET_CONTRACTS
from .helpers import TokenHelpers
from .serializers import contract_schema, token_schema
from ..celery import app


class TokenTask(Task):
    abstract = True

    def __init__(self):
        super().__init__()
        self.token_helpers = TokenHelpers()


@app.task(name=TASK_GET_CONTRACT, base=TokenTask, bind=True)
def get_contract(self, contract_id=None):
    contract = self.token_helpers.get_contract(contract_id)
    if contract is None:
        return {}
    else:
        return contract_schema.dump(contract).data


@app.task(name=TASK_GET_CONTRACTS, base=TokenTask, bind=True)
def get_contracts(self, contract_ids=None, only_listening=True):
    contracts = self.token_helpers.get_contracts(contract_ids, only_listening)
    return contract_schema.dump(contracts, many=True).data


@app.task(name=TASK_INSERT_LOGS, base=TokenTask, bind=True)
def insert_logs(self, logs):
    logs_tokens = self.token_helpers.insert_logs(logs)
    self.token_helpers.commit()
    return [{
        'logs': log_token['logs'],
        'tokens': token_schema.dump(log_token['tokens'], many=True).data
    } for log_token in logs_tokens]

from celery import Task

from .constants import TASK_INSERT_LOGS, TASK_GET_CONTRACTS
from .helpers import TokenHelpers
from .serializers import contract_schema
from ..celery import app


class TokenTask(Task):
    abstract = True

    def __init__(self, session=None):
        super().__init__()
        self.token_helpers = TokenHelpers(session)


@app.task(name=TASK_GET_CONTRACTS, base=TokenTask, bind=True)
def get_contracts(self, only_listening=True):
    contracts = self.token_helpers.get_contracts(only_listening)
    return contract_schema.dump(contracts, many=True).data


@app.task(name=TASK_INSERT_LOGS, base=TokenTask, bind=True)
def insert_logs(self, logs):
    self.token_helpers.insert_logs(logs)
    self.token_helpers.commit()

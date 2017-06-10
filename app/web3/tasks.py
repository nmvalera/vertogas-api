from celery import Task, chord

from .constants import TASK_GET_EVENT_LOGS, TASK_ENRICH_LOG, \
    TASK_FORMAT_LOGS, TASK_ENRICH_LOGS, TASK_GET_LOGS, TASK_GET_ENRICHED_LOGS
from .helpers import Web3Helpers
from .utils import make_filter_param, format_logs
from ..celery import app


class Web3Task(Task):
    abstract = True

    def __init__(self, session=None):
        super().__init__()
        self.web3_helpers = Web3Helpers(session)


@app.task(name=TASK_GET_EVENT_LOGS, base=Web3Task, autoretry_for=(Exception,), default_retry_delay=1, bind=True)
def get_event_logs(self, contract, event, filter_param):
    return self.web3_helpers.get_event_logs(contract, event, filter_param)


@app.task(name=TASK_GET_LOGS)
def get_logs(contract, from_block=None, to_block=None):
    filter_param, from_block, to_block = make_filter_param(contract, from_block, to_block)
    chain = chord(get_event_logs.s(contract, event, filter_param) for event in contract['events'])
    return chain(), from_block, to_block


@app.task(name=TASK_FORMAT_LOGS)
def format_logs(logs, from_block, to_block):
    return format_logs(logs), from_block, to_block


@app.task(name=TASK_ENRICH_LOG, base=Web3Task, autoretry_for=(Exception,), default_retry_delay=1, bind=True)
def enrich_log(self, log, block_number):
    return {**log, 'block': self.web3_helpers.get_block(block_number)}


@app.task(name=TASK_ENRICH_LOGS)
def enrich_logs(logs, from_block, to_block):
    chain = chord(enrich_log.s(log) for log in logs)
    return chain(), from_block, to_block


@app.task(name=TASK_GET_ENRICHED_LOGS)
def get_enriched_logs(contract, from_block=None, to_block=None):
    chain = get_logs.s(contract, from_block, to_block)
    chain |= format_logs.s()
    chain |= enrich_logs.s()
    return contract.id, chain()

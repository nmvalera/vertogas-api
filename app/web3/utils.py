from ..common.constants import FROM_BLOCK_KEY, TO_BLOCK_KEY, BLOCK_NUMBER_KEY


def make_filter_param(contract, from_block=None, to_block=None):
    return {
        FROM_BLOCK_KEY: from_block or contract.last_block + 1,
        TO_BLOCK_KEY: to_block or 'latest',
    }


def format_logs(logs):
    formatted_logs = [{'event_id': event_id, 'log': log} for event_id, logs in logs.items() for log in logs]
    return sorted(formatted_logs,  key=lambda log: log['log'][BLOCK_NUMBER_KEY])

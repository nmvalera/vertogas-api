from ..common import FROM_BLOCK_KEY, TO_BLOCK_KEY, BLOCK_NUMBER_KEY


def make_filter_param(contract, from_block=None, to_block=None):
    filter_param = {
        FROM_BLOCK_KEY: from_block or contract['last_block'] + 1,
        TO_BLOCK_KEY: to_block or 'latest',
    }
    return filter_param


def expand_logs(logs):
    formatted_logs = [{'event_id': log['event_id'], 'log': l} for log in logs for l in log['logs']]
    return sorted(formatted_logs,  key=lambda log: log['log'][BLOCK_NUMBER_KEY])

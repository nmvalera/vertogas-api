from eth_utils import encode_hex

from ..common import FROM_BLOCK_KEY, TO_BLOCK_KEY, BLOCK_NUMBER_KEY, \
    TOKEN_CERTIFICATE_ID_KEY, TOKEN_META_DATA_KEY


def make_filter_param(contract, from_block=None, to_block=None):
    filter_param = {
        FROM_BLOCK_KEY: from_block or contract['last_block'] + 1,
        TO_BLOCK_KEY: to_block or 'latest',
    }
    return filter_param


def expand_logs(logs):
    formatted_logs = [{'event_id': log['event_id'], 'log': l} for log in logs for l in log['logs']]
    return sorted(formatted_logs,  key=lambda log: log['log'][BLOCK_NUMBER_KEY])


def format_log_args(log):
    args = log['args']
    if TOKEN_CERTIFICATE_ID_KEY in args:
        args[TOKEN_CERTIFICATE_ID_KEY] = encode_hex(args[TOKEN_CERTIFICATE_ID_KEY])

    if TOKEN_META_DATA_KEY in args:
        args[TOKEN_META_DATA_KEY] = encode_hex(args[TOKEN_META_DATA_KEY])

    return {**log, 'args': args}

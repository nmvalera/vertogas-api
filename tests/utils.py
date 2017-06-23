from .constants import *


def make_log(event_id, event_name, extra_args):
    args = {
        'certifID': "0x6d01278accde8008e5c8abdc07fad5",
    }
    args.update(extra_args)
    log = {
        'args': args,
        'event': event_name,
        'logIndex': 0,
        'transactionIndex': 0,
        'transactionHash': '0x6d0127880085c8abdc07f5fb21b53ed8b2f5eebe53477b647fd11e6943e8a344',
        'address': CONTRACT_ADDRESS_1,
        'blockHash': '0xde89a5107e263ebb1158ca8366207ebded167848588ca5c3982f2cef85eebcf3',
        'blockNumber': 1802481,
        'block': {
            'timestamp': 1424182926,
        }
    }
    return {
        'event_id': event_id,
        'log': log,
    }


def make_new_certificate_log(event_id, event_name=NEW_CERTIFICATE_EVENT_NAME):
    extra_args = {
        'owner': '0x13377b14b615fff59c8e66288c32365d38181cdb',
        'metaData': 'meta_data',
    }
    return make_log(event_id, event_name, extra_args)


def make_transfer_certificate_log(event_id, event_name=TRANSFER_CERTIFICATE_EVENT_NAME):
    extra_args = {
        'from': '0x13377b14b615fff59c8e66288c32365d38181cdb',
        'to': '0x13377b14b615fff59c8e66288c32365d38181cdb',
    }
    return make_log(event_id, event_name, extra_args)


def make_claim_certificate_log(event_id, event_name=CLAIM_CERTIFICATE_EVENT_NAME):
    extra_args = {
        'from': '0x13377b14b615fff59c8e66288c32365d38181cdb',
    }
    return make_log(event_id, event_name, extra_args)


def make_admin_clean_certificate_log(event_id, event_name=ADMIN_CLEANING_EVENT_NAME):
    extra_args = {}
    return make_log(event_id, event_name, extra_args)


def make_contract(last_block):
    return {
        'address': CONTRACT_ADDRESS_1,
        'abi': CONTRACT_ABI_1,
        'last_block': last_block,
    }

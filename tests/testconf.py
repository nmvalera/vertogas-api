import json

from app.common.constants import NEW_CERTIFICATE_EVENT_NAME, TRANSFER_CERTIFICATE_EVENT_NAME, \
    CLAIM_CERTIFICATE_EVENT_NAME, ADMIN_CLEANING_EVENT_NAME

CONTRACT_ADDRESS = '0x57a0526fbce4183d146be2ef31e16969dacf51bf'
CONTRACT_FAKE_ADDRESS = '0x343deaf9453bcfde30323237abdde4343dff2323'

with open('solidity/%s/abi.json' % CONTRACT_ADDRESS, 'rb') as json_abi:
    CONTRACT_ABI = json_abi.read()

EVENT_NAMES = [
    NEW_CERTIFICATE_EVENT_NAME,
    TRANSFER_CERTIFICATE_EVENT_NAME,
    CLAIM_CERTIFICATE_EVENT_NAME,
    ADMIN_CLEANING_EVENT_NAME,
]

EVENT_ABIS = [
    json.dumps(abi, separators=(',', ':')).encode() for abi in json.loads(CONTRACT_ABI.decode()) if abi['type'] == 'event'
]

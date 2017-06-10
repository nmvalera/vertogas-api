# Convenient constants

# jsonRPC filter parameters key
FROM_BLOCK_KEY = 'fromBlock'
TO_BLOCK_KEY = 'toBlock'

# jsonRPC response keys
EVENT_KEY = 'event'
BLOCK_HASH_KEY = 'blockHash'
BLOCK_NUMBER_KEY = 'blockNumber'
BLOCK_TIMESTAMP_KEY = 'timestamp'
TRANSACTION_HASH_KEY = 'transactionHash'
TRANSACTION_INDEX_KEY = 'transactionIndex'
ARGS_KEY = 'args'

# Smart contract constants
# event names
NEW_CERTIFICATE_EVENT_NAME = 'NewCertificate'
TRANSFER_CERTIFICATE_EVENT_NAME = 'Transfer'
CLAIM_CERTIFICATE_EVENT_NAME = 'Claim'
ADMIN_CLEANING_EVENT_NAME = 'AdminCleaning'

# event inputs
TOKEN_ID_KEY = 'certifID'
TOKEN_OWNER_KEY = 'owner'
TOKEN_META_DATA_KEY = 'metaData'
FROM_ADDRESS_KEY = 'from'
TO_ADDRESS_KEY = 'to'

# Main tasks
TASK_PREFIX = 'main'
TASK_UPDATE_LOGS = '%s.update_logs' % TASK_PREFIX
TASK_UPDATE_ALL_CONTRACTS = '%s.update_all_contracts' % TASK_PREFIX

MAIN_TASKS = [
    TASK_UPDATE_LOGS,
    TASK_UPDATE_ALL_CONTRACTS,
]

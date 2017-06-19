# Convenient constants

# Models constants
# Contract table
CONTRACT_TABLENAME = 'contracts'

# Event table
EVENT_TABLENAME = 'events'
EVENT_NAME_LENGTH = 32

# Event logs table
LOG_TABLENAME = 'logs'

# Token table
TOKEN_TABLENAME = 'tokens'

POWER_PLANT_TABLENAME = 'power_plants'
MIX_TABLENAME = 'mixes'
BIOMASS_TABLENAME = 'biomass'

# celery tasks
TASK_PREFIX = 'tokens'
TASK_INSERT_LOGS = '%s.insert_log' % TASK_PREFIX
TASK_GET_CONTRACT = '%s.get_contract' % TASK_PREFIX
TASK_GET_CONTRACTS = '%s.get_contracts' % TASK_PREFIX

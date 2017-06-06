class DatabaseConfig:
    # Database URI
    DATABASE_URI = "postgresql://postgres:postgres@localhost:5432/postgres"


class ParityServerConfig:
    # Address of the parity server
    PARITY_SERVER_HOST = 'vps412488.ovh.net'
    PARITY_SERVER_PORT = '1935'


class Web3Config(ParityServerConfig):
    # Number of block to wait before inserting an event in the database
    SAFETY_BLOCK_COUNT = 10

class Config(DatabaseConfig, Web3Config):
    pass

config = Config
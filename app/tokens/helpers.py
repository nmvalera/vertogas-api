import json

from eth_utils import encode_hex
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from .models import Base
from .models import Contract, Event, Log, Token
from .serializers import rpc_loader_schema
from .session import session as default_session
from .utils import insert_table
from ..common.constants import NEW_CERTIFICATE_EVENT_NAME, TRANSFER_CERTIFICATE_EVENT_NAME, \
    CLAIM_CERTIFICATE_EVENT_NAME, ADMIN_CLEANING_EVENT_NAME, \
    TOKEN_ID_KEY, TOKEN_OWNER_KEY, TOKEN_META_DATA_KEY, \
    FROM_ADDRESS_KEY, TO_ADDRESS_KEY, TO_BLOCK_KEY


class TokenHelpers:
    def __init__(self, session=default_session):
        self.session = session

    def _add(self, obj):
        self.session.add(obj)

    def commit(self):
        self.session.commit()

    def flush(self):
        self.session.flush()

    def rollback(self):
        self.session.rollback()

    def close(self):
        self.session.close()

    def init_db(self):
        Base.metadata.drop_all(self.session.get_bind())
        Base.metadata.create_all(self.session.get_bind())
        return Base.metadata.tables

    def drop_db(self):
        Base.metadata.drop_all(self.session.get_bind())
        return Base.metadata.tables

    def insert_table(self, path, table_name):
        con = self.session.get_bind().connect()
        insert_table(path, table_name, con)

    def insert_contract(self, address, contract_abi):
        """
        Insert a new contract in the database
        :param address: contract's address in the Blockchain
        :param contract_abi: contract's abi
        :return: inserted contract
        """
        contract = Contract(address=address.lower(), abi=contract_abi)
        self._add(contract)
        self.flush()

        # add an entry in the database for every event in the contract abi
        contract_abi = json.loads(contract_abi.decode())
        for abi in contract_abi:
            if abi['type'] == 'event':
                self.insert_event(contract.id, abi)

        return contract

    def insert_event(self, contract_id, event_abi):
        """
        Insert a new event filter in the database
        :param contract_id: id of the contract to add an event filter on
        :param event_abi: abi of the event to add
        :return: inserted event
        """
        name = event_abi['name']
        event_abi = json.dumps(event_abi, separators=(',', ':')).encode()
        event = Event(contract_id=contract_id, name=name, abi=event_abi)
        self._add(event)
        self.flush()
        return event

    def get_contract(self, contract_id=None):
        if contract_id:
            return self.session.query(Contract).filter_by(id=contract_id).first()
        else:
            return self.get_less_updated_contract()

    def get_less_updated_contract(self):
        """
        Get the contract that is listening with the lower last block number
        :return: contract
        """
        query = self.session. \
            query(Contract). \
            filter(Contract.is_listening). \
            order_by(Contract.last_block)
        return query.first()

    def get_event(self, event_id):
        return self.session.query(Event).filter_by(id=event_id).first()

    def get_token(self, **kwargs):
        return self.session.query(Token).filter_by(**kwargs).first()

    def get_contracts(self, contract_ids=None, only_listening=True):
        query = self.session. \
            query(Contract)

        if contract_ids is not None:
            query = query.filter(Contract.id.in_(contract_ids))

        elif only_listening:
            query = query.filter(Contract.is_listening)

        return query.all()

    def get_events(self, contract_id):
        query = self.session. \
            query(Event). \
            filter_by(contract_id=contract_id)

        return query.all()

    def get_logs(self, contract_id=None, token_id=None):

        query = self.session. \
            query(Log)

        if contract_id is not None:
            query = query.filter(Contract.id == contract_id). \
                filter(and_(Contract.id == Event.contract_id, Event.id == Log.event_id))

        if token_id is not None:
            query = query.filter_by(token_id=token_id)

        query = query.order_by(Log.block_number)

        return query.all()

    def get_tokens(self, contract_id, power_plant_id=None):
        query = self.session. \
            query(Token). \
            filter_by(contract_id=contract_id)

        if power_plant_id is not None:
            query = query.filter_by(power_plant_id=power_plant_id)

        return query.all()

    def start_listening(self, contract_id):
        """
        Start listening events for a contract
        :param contract_id: contract to start listening for
        :return: contract stop listen
        """
        contract = self.get_contract(contract_id)
        if contract:
            contract.is_listening = True
            self.flush()
            return contract
        return

    def stop_listening(self, contract_id):
        """
        Stop listening events for a contract
        :param contract_id: contract to stop listening for
        :return:
        """
        contract = self.get_contract(contract_id)
        if contract:
            contract.is_listening = False
            self.flush()
            return contract
        return

    def set_last_block(self, contract_id, last_block):
        """
        Set the value of the last block which data has been parsed for a contract
        :param contract_id: id of the contract to be set
        :param last_block: last block number 
        """
        contract = self.get_contract(contract_id)
        contract.last_block = last_block
        self.flush()

    def create_token(self, contract_id, certificate_id, meta_data, owner):
        """
        Create a new token
        :param contract_id: id of the contract the token has been instantiated by        
        :param certificate_id: token's certificate_id in the Blockchain
        :param contract_id: id of the contract that generated the token
        :param meta_data: hash of the me
        :param owner: owner of the created token
        :return: created token
        """
        token = Token(certificate_id=certificate_id,
                      contract_id=contract_id,
                      meta_data=meta_data,
                      owner=owner)
        self._add(token)
        try:
            self.flush()
        except IntegrityError:
            self.rollback()
            return
        return token

    def transfer_token(self, contract_id, certificate_id, from_address, to_address):
        """
        Transfer a token
        :param contract_id: id of the contract the token has been instantiated by        
        :param certificate_id: id of the token to transfer
        :param from_address: address of the old owner
        :param to_address: address of the new owner
        :return: token on the new owner
        """
        token = self.get_token(contract_id=contract_id, certificate_id=certificate_id)

        # ensure from_address corresponds to the owner address
        if token and token.owner == from_address:
            token.owner = to_address
            self.flush()
            return token
        return

    def claim_token(self, contract_id, certificate_id, claimer_address=None):
        """
        Claim a tis_claimedoken
        :param contract_id: id of the contract the token has been instantiated by        
        :param certificate_id: id of the token to claim
        :param claimer_address: claimer's address in the Blockchain
        :return: claimed token
        """
        token = self.get_token(contract_id=contract_id, certificate_id=certificate_id)
        contract = self.get_contract(contract_id)

        # ensure claimer's address corresponds to the owner address or is admin
        if token and (claimer_address in [token.owner, contract.admin_address]):
            token.is_claimed = True
            token.claimer = claimer_address
            self.flush()
            return token
        return

    def insert_log(self, log):
        """
        Insert an event log in the database and perform corresponding modification
        :param log: dict log as received from the RPC call
        :return: Log object
        """
        event_id = log['event_id']
        log = log['log']
        block = log['block']

        event = self.get_event(event_id)
        
        # ensure the log corresponds to the expected event
        if (event is not None) and (log['event'] == event.name) and (log['address'] == event.contract.address):
            # format log arguments
            args = {k: encode_hex(v) for k, v in log['args'].items()}

            # perform modifications on tokens table
            if event.name == NEW_CERTIFICATE_EVENT_NAME:
                token = self.create_token(event.contract.id,
                                          args[TOKEN_ID_KEY],
                                          args[TOKEN_META_DATA_KEY],
                                          args[TOKEN_OWNER_KEY])

            elif event.name == TRANSFER_CERTIFICATE_EVENT_NAME:
                token = self.transfer_token(event.contract.id,
                                            args[TOKEN_ID_KEY],
                                            args[FROM_ADDRESS_KEY],
                                            args[TO_ADDRESS_KEY])

            elif event.name == CLAIM_CERTIFICATE_EVENT_NAME:
                token = self.claim_token(event.contract.id,
                                         args[TOKEN_ID_KEY],
                                         args[FROM_ADDRESS_KEY])

            elif event.name == ADMIN_CLEANING_EVENT_NAME:
                token = self.claim_token(event.contract.id,
                                         args[TOKEN_ID_KEY])

            else:
                token = None

            # Add the log to the logs table
            if token is not None:
                self._add(rpc_loader_schema(event, token, block).load(log).data)
                self.flush()
                return token
        return

    def insert_logs(self, logs):
        """
        Insert a batch of logs
        :param logs: list of logs to insert (logs must ordered by ascending block number)
        :return: list of modified tokens
        """
        if isinstance(logs, list):
            logs_tokens = [self.insert_logs(log) for log in logs]
            return [log_token for log_token in logs_tokens if log_token is not None]

        else:
            # compute parameters of interest
            contract_id = logs['contract']['id']
            to_block = logs['filter_param'][TO_BLOCK_KEY]
            logs = logs['data']

            if self.get_contract(contract_id) is not None:
                # calculate the set of token ids that have been modified
                token_ids = [getattr(self.insert_log(log), 'id', None) for log in logs]
                if None in token_ids:
                    token_ids.remove(None)
                token_ids = list(set(token_ids))  # get unique ids
                self.set_last_block(contract_id, to_block)

                # return the current state of each modified token
                return {
                    'logs': logs,
                    'tokens': [self.get_token(id=token_id) for token_id in token_ids],
                }
            return

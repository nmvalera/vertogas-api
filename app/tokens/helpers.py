import json

from eth_utils import encode_hex
from sqlalchemy import and_

from .models import Base
from .models import Contract, Event, Log, Token
from .serializers import rpc_response_schema
from .session import create_session_maker
from ..common.constants import NEW_CERTIFICATE_EVENT_NAME, TRANSFER_CERTIFICATE_EVENT_NAME, \
    CLAIM_CERTIFICATE_EVENT_NAME, ADMIN_CLEANING_EVENT_NAME, \
    TOKEN_ID_KEY, TOKEN_OWNER_KEY, TOKEN_META_DATA_KEY, \
    FROM_ADDRESS_KEY, TO_ADDRESS_KEY


class TokenHelpers:
    def __init__(self, session=None):
        if isinstance(session, str) or session is None:
            self.session = create_session_maker(session)()
        else:
            self.session = session

    def _add(self, obj):
        self.session.add(obj)

    def commit(self):
        self.session.commit()

    def flush(self):
        self.session.flush()

    def init_db(self):
        Base.metadata.drop_all(self.session.get_bind())
        #self.session.get_bind().execute("drop schema if exists public cascade")
        Base.metadata.create_all(self.session.get_bind())

        return Base.metadata.tables

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

    def get_contract(self, contract_id):
        return self.session.query(Contract).filter_by(id=contract_id).first()

    def get_event(self, event_id):
        return self.session.query(Event).filter_by(id=event_id).first()

    def get_token(self, contract_id, certificate_id):
        return self.session.query(Token).filter_by(contract_id=contract_id, certificate_id=certificate_id).first()

    def get_contracts(self):
        query = self.session. \
            query(Contract). \
            filter(Contract.is_listening)
        return query.all()

    def get_logs(self, contract_id):
        query = self.session. \
            query(Log). \
            filter(Contract.id == contract_id). \
            filter(and_(Contract.id == Event.contract_id, Event.id == Log.event_id)). \
            order_by(Log.block_number)
        return query.all()

    def get_tokens(self, contract_id):
        contract = self.get_contract(contract_id)
        if contract:
            return contract.tokens.all()
        return []

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

    def set_last_block(self, contract, last_block):
        """
        Set the value of the last block which data has been parsed for a contract
        :param contract: contract to be set
        :param last_block: last block number 
        """
        contract.last_block = last_block
        self.flush()

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
                      meta_data=meta_data.encode(),
                      owner=owner)
        self._add(token)
        self.flush()
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
        token = self.get_token(contract_id, certificate_id)
        if token:
            # ensure from_address corresponds to the owner address
            assert token.owner == from_address
            token.owner = to_address
            self.flush()
        return token

    def claim_token(self, contract_id, certificate_id, claimer_address=None):
        """
        Claim a token
        :param contract_id: id of the contract the token has been instantiated by        
        :param certificate_id: id of the token to claim
        :param claimer_address: claimer's address in the Blockchain
        :return: claimed token
        """
        token = self.get_token(contract_id, certificate_id)
        if token:
            assert claimer_address is None or token.owner == claimer_address
            token.is_claimed = True
            token.claimer = claimer_address
            self.flush()
        return token

    def insert_log(self, event_id, block, log):
        """
        Insert an event log in the database and perform corresponding modification
        :param event_id: id of the event the log corresponds to
        :param block: information about the block the log belongs to
        :param log: dict log as received from the RPC call
        :return: Log object
        """
        event = self.get_event(event_id)
        
        # ensure the log corresponds to the expected event
        assert event is not None, \
            'There is no event with id=%s' % event_id
        assert event.name == log['event'], \
            'Event %s type is not correct (expected "%s")' % (event_id, log['event'])
        assert event.contract.address == log['address'], \
            'Event %s contract\'s address is not correct  (expected %s)' % (event_id, log['address'])

        # format log arguments
        args = {k: encode_hex(v) for k, v in log['args'].items()}
        
        # perform modifications on tokens table
        if event.name == NEW_CERTIFICATE_EVENT_NAME:
            token = self.create_token(event.contract.id, args[TOKEN_ID_KEY], args[TOKEN_META_DATA_KEY], args[TOKEN_OWNER_KEY])

        elif event.name == TRANSFER_CERTIFICATE_EVENT_NAME:
            token = self.transfer_token(event.contract.id, args[TOKEN_ID_KEY], args[FROM_ADDRESS_KEY], args[TO_ADDRESS_KEY])

        elif event.name == CLAIM_CERTIFICATE_EVENT_NAME:
            token = self.claim_token(event.contract.id, args[TOKEN_ID_KEY], args[FROM_ADDRESS_KEY])

        elif event.name == ADMIN_CLEANING_EVENT_NAME:
            token = self.claim_token(event.contract.id, args[TOKEN_ID_KEY])

        else:
            token = None

        # Add the log to the logs table
        log = rpc_response_schema(event, token, block).load(log).data
        self._add(log)
        self.flush()

        return log

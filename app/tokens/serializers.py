import datetime
import json

from eth_utils import encode_hex
from marshmallow import Schema, fields, post_load

from .models import Log
from ..common.constants import BLOCK_HASH_KEY, BLOCK_NUMBER_KEY, BLOCK_TIMESTAMP_KEY, \
    TRANSACTION_HASH_KEY, TRANSACTION_INDEX_KEY, \
    ARGS_KEY


class EventSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class ContractSchema(Schema):
    id = fields.Int()
    address = fields.Str()
    is_listening = fields.Boolean()
    last_block = fields.Integer()
    abi = fields.Str()
    events = fields.Nested(EventSchema, many=True)


contract_schema = ContractSchema()


class LogSchema(Schema):
    name = fields.Str()
    block_number = fields.Int()
    args = fields.Str()


log_schema = LogSchema()


class TokenSchema(Schema):
    id = fields.Int()
    certificate_id = fields.Str()
    meta_data = fields.Str()
    owner = fields.Str()
    is_claimed = fields.Bool()
    claimer = fields.Str()

token_schema = TokenSchema()


class RPCLoaderSchema(Schema):
    """
    Allows to load a log dictionary into a SQLAlchemy Log object 
    """
    block_hash = fields.Str(
        load_from=BLOCK_HASH_KEY,
        required=True
    )
    block_number = fields.Int(
        load_from=BLOCK_NUMBER_KEY,
        required=True
    )

    transaction_hash = fields.Str(
        load_from=TRANSACTION_HASH_KEY,
        required=True
    )
    transaction_index = fields.Int(
        load_from=TRANSACTION_INDEX_KEY,
        required=True
    )

    args = fields.Method(deserialize='load_args', load_from=ARGS_KEY)

    @staticmethod
    def load_args(args):
        # Reformat jsonRPC response args in hex format (for readability)
        return json.dumps({k: encode_hex(v) for k, v in args.items()}, separators=(',', ':')).encode()

    @post_load
    def wrap_log(self, log):
        event_id = self.context.get('event').id
        if self.context.get('token'):
            token_id = self.context.get('token').id
        else:
            token_id = None
        timestamp = datetime.datetime.fromtimestamp(log['block'][BLOCK_TIMESTAMP_KEY])
        return Log(event_id=event_id, token_id=token_id, timestamp=timestamp, **log)


def rpc_loader_schema(event, token, block):
    schema = RPCLoaderSchema()
    schema.context['event'] = event
    schema.context['block'] = block
    schema.context['token'] = token
    return schema

import datetime
import json

from marshmallow import Schema, fields, post_load

from .constants import CERTIFICATE_ID_KEY, IS_CLAIMED_KEY, META_DATA_KEY
from .models import Log
from ..common.constants import BLOCK_HASH_KEY, BLOCK_NUMBER_KEY, BLOCK_TIMESTAMP_KEY, \
    TRANSACTION_HASH_KEY, TRANSACTION_INDEX_KEY, \
    ARGS_KEY, ISSUED_DATE_KEY


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


class LogSchemaCelery(Schema):
    block_number = fields.Int(dump_to=BLOCK_NUMBER_KEY)
    timestamp = fields.DateTime()
    args = fields.Str()


log_schema = LogSchemaCelery()


class LogSchemaAPI(Schema):
    block_number = fields.Int(dump_to=BLOCK_NUMBER_KEY)
    timestamp = fields.DateTime()
    args = fields.Function(lambda obj: json.loads(obj.args.decode()))

    event = fields.Nested(EventSchema)


log_schema_api = LogSchemaAPI()


class BiomassSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class MixSchema(Schema):
    ratio = fields.Int()
    biomass = fields.Nested(BiomassSchema)


class TokenSchemaCelery(Schema):
    id = fields.Int()

    certificate_id = fields.Str()
    meta_data = fields.Str()

    owner = fields.Str()

    is_claimed = fields.Bool()
    claimer = fields.Str()


token_schema = TokenSchemaCelery()


class TokenSchemaAPI(Schema):
    id = fields.Int()

    certificate_id = fields.Str(dump_to=CERTIFICATE_ID_KEY)
    meta_data = fields.Str(dump_to=META_DATA_KEY)

    issued_date = fields.Str(dump_to=ISSUED_DATE_KEY)
    owner = fields.Str()

    is_claimed = fields.Bool(dump_to=IS_CLAIMED_KEY)
    claimer = fields.Str()


token_schema_api = TokenSchemaAPI()


class PowerPlantSchemaAPI(Schema):
    id = fields.Int()
    name = fields.Str()
    owner = fields.Str()
    meta_data = fields.Str(dump_to=META_DATA_KEY)

    mix = fields.Nested(MixSchema, many=True)

    tokens = fields.Nested(TokenSchemaAPI, many=True)


power_plant_schema_api = PowerPlantSchemaAPI()


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
        args = json.dumps(args, separators=(',', ':')).encode()
        return args

    @post_load
    def wrap_log(self, log):
        event_id = self.context.get('event').id
        if self.context.get('token'):
            token_id = self.context.get('token').id
        else:
            token_id = None
        timestamp = datetime.datetime.fromtimestamp(self.context.get('block')[BLOCK_TIMESTAMP_KEY])
        return Log(event_id=event_id, token_id=token_id, timestamp=timestamp, **log)


def rpc_loader_schema(event, token, block):
    schema = RPCLoaderSchema()
    schema.context['event'] = event
    schema.context['block'] = block
    schema.context['token'] = token
    return schema

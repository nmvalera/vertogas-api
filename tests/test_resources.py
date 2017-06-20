import pytest

from app import create_app
from app.common.constants import VERTOGAS_URL_PREFIX, POWER_PLANTS_RESOURCE, TOKENS_RESOURCE, LOGS_RESOURCE, \
    NEW_CERTIFICATE_EVENT_NAME, TRANSFER_CERTIFICATE_EVENT_NAME, \
    CLAIM_CERTIFICATE_EVENT_NAME, ADMIN_CLEANING_EVENT_NAME, \
    FROM_ADDRESS_KEY, TO_ADDRESS_KEY, TOKEN_OWNER_KEY
from app.tokens.constants import BLOCK_NUMBER_KEY, META_DATA_KEY, IS_CLAIMED_KEY, CERTIFICATE_ID_KEY
from app.tokens.helpers import TokenHelpers
from app.tokens.serializers import contract_schema
from app.web3.helpers import Web3Helpers
from .constants import OWNER_ADDRESS, \
    CONTRACT_ADDRESS, CONTRACT_ABI


def setup_module(module):
    """Setup database for testing"""
    token_helpers = TokenHelpers()
    token_helpers.init_db()
    token_helpers.insert_contract(CONTRACT_ADDRESS, CONTRACT_ABI)
    token_helpers.commit()
    token_helpers.insert_data(
        ['data/power_plants.pickle', 'data/biomass.pickle', 'data/mixes.pickle'],
        ['power_plants', 'biomass', 'mixes']
    )
    web3_helpers = Web3Helpers()
    contracts = contract_schema.dump(token_helpers.get_contracts([1]), many=True).data
    token_helpers.insert_logs(web3_helpers.get_logs(contracts, 0, 2042415))
    token_helpers.commit()


def teardown_module(module):
    """Tear down database"""
    token_helpers = TokenHelpers()
    token_helpers.drop_db()
    token_helpers.commit()
    token_helpers.close()


@pytest.fixture
def app():
    return create_app(register_blueprints=True)


@pytest.mark.usefixtures('client_class')
class TestSuite:
    def _test_get_status200(self, endpoint):
        response = self.client.get(endpoint)
        assert response.status_code == 200
        return response

    def _test_event(self, event):
        assert 'id' in event
        assert 'name' in event

    def _test_log_args(self, args, event_name):
        assert CERTIFICATE_ID_KEY in args
        if event_name == NEW_CERTIFICATE_EVENT_NAME:
            assert META_DATA_KEY in args
            assert TOKEN_OWNER_KEY in args

        elif event_name == TRANSFER_CERTIFICATE_EVENT_NAME:
            assert FROM_ADDRESS_KEY in args
            assert TO_ADDRESS_KEY in args

        elif event_name == CLAIM_CERTIFICATE_EVENT_NAME:
            assert FROM_ADDRESS_KEY in args

        elif event_name == ADMIN_CLEANING_EVENT_NAME:
            pass

        else:
            assert False

    def _test_log(self, log):
        for key in [BLOCK_NUMBER_KEY, 'timestamp', 'args', 'event']:
            assert key in log
        self._test_event(log['event'])
        self._test_log_args(log['args'], log['event']['name'])


    def _test_get_logs(self, token_id):
        response = self._test_get_status200('%s%s/%s' % (VERTOGAS_URL_PREFIX, LOGS_RESOURCE, token_id))
        logs = response.json
        assert isinstance(logs, list)
        for log in logs:
            self._test_log(log)
        return logs

    def test_get_logs(self):
        logs = self._test_get_logs(1)
        assert len(logs) == 4

    def _test_token(self, token):
        for key in ['id', CERTIFICATE_ID_KEY, META_DATA_KEY, 'owner', IS_CLAIMED_KEY, 'claimer']:
            assert key in token

    def _test_tokens(self, tokens):
        assert isinstance(tokens, list)
        for token in tokens:
            self._test_token(token)

    def _test_get_tokens_by_power_plant(self, power_plant_id):
        response = self._test_get_status200('%s%s/power_plant/%s' %
                                            (VERTOGAS_URL_PREFIX, TOKENS_RESOURCE, power_plant_id))
        tokens = response.json
        self._test_tokens(tokens)
        return tokens

    def _test_get_tokens_by_owner(self, owner):
        response = self._test_get_status200('%s%s/owner/%s' % (VERTOGAS_URL_PREFIX, TOKENS_RESOURCE, owner))
        tokens = response.json
        self._test_tokens(tokens)
        return tokens

    def test_get_tokens(self):
        tokens = self._test_get_tokens_by_power_plant(3)
        assert len(tokens) > 0
        self._test_get_tokens_by_owner(OWNER_ADDRESS)
        assert len(tokens) == 1

    def _test_mix(self, mix):
        assert isinstance(mix, list)
        assert len(mix) > 0
        for element in mix:
            assert 'ratio' in element
            assert 'biomass' in element
        assert sum([element['ratio'] for element in mix]) == 100

    def _test_power_plant(self, power_plant):
        for key in ['id', META_DATA_KEY, 'owner', 'name', 'mix', 'tokens']:
            assert key in power_plant
        self._test_mix(power_plant['mix'])
        self._test_tokens(power_plant['tokens'])

    def test_get_power_plants(self):
        response = self._test_get_status200('%s%s/%s' % (VERTOGAS_URL_PREFIX, POWER_PLANTS_RESOURCE, OWNER_ADDRESS))
        assert isinstance(response.json, list)
        assert len(response.json) > 0
        for power_plant in response.json:
            self._test_power_plant(power_plant)

        response = self._test_get_status200('%s%s' % (VERTOGAS_URL_PREFIX, POWER_PLANTS_RESOURCE))
        assert isinstance(response.json, list)
        assert len(response.json) > 0
        for power_plant in response.json:
            self._test_power_plant(power_plant)

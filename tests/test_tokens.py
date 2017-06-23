import pytest
from sqlalchemy.exc import IntegrityError

from app.tokens.helpers import TokenHelpers
from app.tokens.models import Contract, Event
from .constants import CONTRACT_ADDRESS_1, CONTRACT_FAKE_ADDRESS, CONTRACT_ABI_1, \
    EVENT_NAMES, EVENT_ABIS
from .utils import make_new_certificate_log, make_transfer_certificate_log, make_claim_certificate_log, \
    make_admin_clean_certificate_log


def setup_module(module):
    """Setup database for testing"""
    token_helpers = TokenHelpers()
    token_helpers.init_db()
    token_helpers.commit()


def teardown_module(module):
    """Tear down database"""
    token_helpers = TokenHelpers()
    token_helpers.drop_db()
    token_helpers.commit()
    token_helpers.close()


def _test_insert_new_contract(contract_address, contract_abi):
    token_helpers = TokenHelpers()
    contracts_count = len(token_helpers.get_contracts())
    contract = token_helpers.insert_contract(contract_address, contract_abi)
    token_helpers.commit()
    assert len(token_helpers.get_contracts()) == contracts_count + 1
    contract = token_helpers.get_contract(contract.id)
    assert isinstance(contract, Contract)
    assert contract.abi == contract_abi
    assert contract.is_listening
    assert contract.last_block == -1
    assert contract.events.count() == len(EVENT_NAMES)
    for event, name, abi in zip(contract.events, EVENT_NAMES, EVENT_ABIS):
        assert event.name == name
        assert event.abi == abi


def _test_insert_existing_contract(contract_address, contract_abi):
    token_helpers = TokenHelpers()
    contracts_count = len(token_helpers.get_contracts())
    with pytest.raises(IntegrityError):
        token_helpers.insert_contract(contract_address, contract_abi)
    token_helpers.rollback()
    token_helpers.commit()
    assert len(token_helpers.get_contracts()) == contracts_count


def test_insert_contract():
    for contract_address in [CONTRACT_ADDRESS_1, CONTRACT_FAKE_ADDRESS]:
        _test_insert_new_contract(contract_address, CONTRACT_ABI_1)
    _test_insert_existing_contract(CONTRACT_ADDRESS_1, CONTRACT_ABI_1)


def test_insert_table():
    token_helpers = TokenHelpers()
    token_helpers.insert_data(
        ['data/power_plants_test.pickle', 'data/biomass_test.pickle', 'data/mixes_test.pickle'],
        ['power_plants', 'biomass', 'mixes']
    )
    token_helpers.commit()


def _test_get_contract(contract_id):
    token_helpers = TokenHelpers()
    contract = token_helpers.get_contract(contract_id)
    assert isinstance(contract, Contract) or contract is None


def test_get_contract():
    for contract_id in range(10):
        _test_get_contract(contract_id)


def _test_get_event(event_id):
    token_helpers = TokenHelpers()
    event = token_helpers.get_event(event_id)
    assert isinstance(event, Event) or event is None


def test_get_event():
    for i in range(20):
        _test_get_event(i)


def _test_stop_listening(contract_id):
    token_helpers = TokenHelpers()
    token_helpers.stop_listening(contract_id)
    token_helpers.commit()
    assert not token_helpers.get_contract(contract_id).is_listening


def _test_start_listening(contract_id):
    token_helpers = TokenHelpers()
    token_helpers.start_listening(contract_id)
    token_helpers.commit()
    assert token_helpers.get_contract(contract_id).is_listening


def test_stop_start_listening():
    for contract_id in range(1, 3):
        _test_stop_listening(contract_id)
        _test_start_listening(contract_id)


def _test_set_last_block(contract_id, new_last_block):
    token_helpers = TokenHelpers()
    contract = token_helpers.get_contract(contract_id)
    former_last_block = contract.last_block
    token_helpers.set_last_block(contract_id, new_last_block)
    token_helpers.commit()
    assert token_helpers.get_contract(contract_id).last_block == new_last_block
    token_helpers.set_last_block(contract_id, former_last_block)
    token_helpers.commit()
    assert token_helpers.get_contract(contract_id).last_block == former_last_block


def test_set_last_block():
    _test_set_last_block(1, 124343)


def _test_create_new_token(contract_id, certificate_id, meta_data, owner):
    token_helpers = TokenHelpers()
    tokens_count = len(token_helpers.get_tokens(contract_id))
    token = token_helpers.create_token(contract_id, certificate_id, meta_data, owner)
    assert token is not None
    token_helpers.commit()
    assert len(token_helpers.get_tokens(contract_id)) == tokens_count + 1
    token = token_helpers.get_token(id=token.id)
    assert token.contract_id == contract_id
    assert token.meta_data == meta_data
    assert token.owner == owner
    assert not token.is_claimed
    assert token.claimer is None


def _test_create_existing_token(contract_id, certificate_id, meta_data, owner):
    token_helpers = TokenHelpers()
    tokens_count = len(token_helpers.get_tokens(contract_id))
    assert token_helpers.create_token(contract_id, certificate_id, meta_data, owner) is None
    assert len(token_helpers.get_tokens(contract_id)) == tokens_count


def test_create_token():
    certificate_ids = ['beef', 'babe']
    contract_ids = [1, 2]
    meta_data = 'meta_data'
    owner = '0x123434314'
    for certificate_id in certificate_ids:
        for contract_id in contract_ids:
            _test_create_new_token(contract_id, certificate_id, meta_data, owner)
    _test_create_existing_token(1, 'beef', 'meta_data_2', '0x123434314')


def _test_token_content_equals(t1, t2):
    assert t1.certificate_id == t2.certificate_id
    assert t1.meta_data == t2.meta_data


def _test_authorized_transfer_token(contract_id, certificate_id, from_address, to_address):
    token_helpers = TokenHelpers()
    token = token_helpers.get_token(contract_id=contract_id, certificate_id=certificate_id)
    token_helpers.transfer_token(contract_id, certificate_id, from_address, to_address)
    token_helpers.commit()
    transferred_token = token_helpers.get_token(id=token.id)
    assert transferred_token.owner == to_address
    _test_token_content_equals(transferred_token, token)


def _test_unauthorized_transfer_token(contract_id, certificate_id, from_address, to_address):
    token_helpers = TokenHelpers()
    token = token_helpers.get_token(contract_id=contract_id, certificate_id=certificate_id)
    token_helpers.transfer_token(contract_id, certificate_id, from_address, to_address)
    token_helpers.commit()
    transferred_token = token_helpers.get_token(id=token.id)
    assert transferred_token.owner == token.owner
    _test_token_content_equals(token, transferred_token)


def test_transfer_token():
    contract_id = 1
    certificate_id = 'babebabe'
    meta_data = 'meta_data'
    valid_from_address = '0x1ae2bc32a8cc91'
    invalid_from_address = '0x78ca24de829aac90'
    to_address = '0x1ae2bc32a8cc91'

    token_helpers = TokenHelpers()
    token_helpers.create_token(contract_id, certificate_id, meta_data, valid_from_address)
    token_helpers.commit()
    _test_unauthorized_transfer_token(contract_id, certificate_id, invalid_from_address, to_address)
    _test_authorized_transfer_token(contract_id, certificate_id, valid_from_address, to_address)


def _test_authorized_claim_token(contract_id, certificate_id, claimer_address):
    token_helpers = TokenHelpers()
    token = token_helpers.get_token(contract_id=contract_id, certificate_id=certificate_id)
    token_helpers.claim_token(contract_id, certificate_id, claimer_address)
    token_helpers.commit()
    claimed_token = token_helpers.get_token(id=token.id)
    assert claimed_token.is_claimed
    assert claimed_token.claimer == claimer_address
    _test_token_content_equals(token, claimed_token)


def _test_unauthorized_claim_token(contract_id, certificate_id, claimer_address):
    token_helpers = TokenHelpers()
    token = token_helpers.get_token(contract_id=contract_id, certificate_id=certificate_id)
    token_helpers.claim_token(contract_id, certificate_id, claimer_address)
    token_helpers.commit()
    claimed_token = token_helpers.get_token(id=token.id)
    assert claimed_token.owner == token.owner
    assert not claimed_token.is_claimed
    _test_token_content_equals(token, claimed_token)


def test_claim_token():
    contract_id = 1
    certificate_id = 'beefbeef'
    meta_data = 'meta_data'
    valid_claimer_address = '0x1ae2bc32a8cc91'
    invalid_claimer_address = '0x78ca24de829aac90'

    token_helpers = TokenHelpers()
    token_helpers.create_token(contract_id, certificate_id, meta_data, valid_claimer_address)
    token_helpers.commit()
    _test_unauthorized_claim_token(contract_id, certificate_id, invalid_claimer_address)
    _test_authorized_claim_token(contract_id, certificate_id, valid_claimer_address)


def _test_invalid_log_insertion(log):
    token_helpers = TokenHelpers()
    assert token_helpers.insert_log(log) is None
    token_helpers.commit()


def _test_valid_log_insertion(log):
    token_helpers = TokenHelpers()
    assert token_helpers.insert_log(log) is not None
    token_helpers.commit()


def test_insert_log():
    _test_invalid_log_insertion(make_new_certificate_log(10))  # event_id does not exist
    for i in [2, 3, 4]:
        _test_invalid_log_insertion(make_new_certificate_log(i))  # event name does not match
    _test_invalid_log_insertion(make_new_certificate_log(5))  # contract address does not match
    _test_valid_log_insertion(make_new_certificate_log(1))

    for i in [1, 3, 4]:
        _test_invalid_log_insertion(make_transfer_certificate_log(i))  # event name does not match
    _test_valid_log_insertion(make_transfer_certificate_log(2))

    for i in [1, 2, 4]:
        _test_invalid_log_insertion(make_claim_certificate_log(i))  # event name does not match
    _test_valid_log_insertion(make_claim_certificate_log(3))

    for i in [1, 2, 3]:
        _test_invalid_log_insertion(make_admin_clean_certificate_log(i))  # event name does not match
    _test_valid_log_insertion(make_admin_clean_certificate_log(4))

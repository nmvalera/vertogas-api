from sqlalchemy import Column, String, Integer, Boolean, LargeBinary, DateTime, \
    ForeignKey, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from .constants import CONTRACT_TABLENAME, \
    EVENT_TABLENAME, EVENT_NAME_LENGTH, \
    LOG_TABLENAME, \
    POWER_PLANT_TABLENAME, MIX_TABLENAME, BIOMASS_TABLENAME, \
    TOKEN_TABLENAME

Base = declarative_base()


class Contract(Base):
    """
    Contains contract description information
    """
    __tablename__ = CONTRACT_TABLENAME
    __table_args__ = (UniqueConstraint('address'),)

    id = Column(Integer, primary_key=True)

    address = Column(String, unique=True)

    abi = Column(LargeBinary)

    admin_address = Column(String, unique=True)

    is_listening = Column(Boolean, default=True)
    last_block = Column(Integer, default=-1)

    events = relationship('Event', back_populates='contract', lazy='dynamic')
    tokens = relationship('Token', back_populates='contract', lazy='dynamic')


class Event(Base):
    """
    Contains event description information
    """
    __tablename__ = EVENT_TABLENAME
    __table_args__ = (UniqueConstraint('contract_id', 'name'),)

    id = Column(Integer, primary_key=True)

    contract_id = Column(Integer, ForeignKey('%s.id' % CONTRACT_TABLENAME))
    contract = relationship('Contract', back_populates='events')

    name = Column(String(EVENT_NAME_LENGTH))

    abi = Column(LargeBinary)

    logs = relationship('Log', back_populates='event', lazy='dynamic')

    def __repr__(self):
        return '<Event %s>' % self.name


class Log(Base):
    """
    Contains information about event logs
    """
    __tablename__ = LOG_TABLENAME
    __table_args__ = (
        UniqueConstraint('event_id', 'token_id', 'block_number'),
    )

    id = Column(Integer, primary_key=True)

    event_id = Column(Integer, ForeignKey('%s.id' % EVENT_TABLENAME))
    event = relationship('Event', back_populates='logs')

    token_id = Column(Integer, ForeignKey('%s.id' % TOKEN_TABLENAME))
    token = relationship('Token', back_populates='logs')

    block_number = Column(Integer)
    block_hash = Column(String)

    transaction_hash = Column(String)
    transaction_index = Column(Integer)

    timestamp = Column(DateTime)

    args = Column(LargeBinary)

    def __repr__(self):
        return '<Log id=%s (%s)>' % (self.id, self.event)


class PowerPlant(Base):
    __tablename__ = POWER_PLANT_TABLENAME
    __table_args__ = (Index('%s.owner_index' % POWER_PLANT_TABLENAME, 'contract_id', 'owner'),)

    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('%s.id' % CONTRACT_TABLENAME), nullable=False, default=1)

    meta_data = Column(String, unique=True)

    name = Column(String)

    owner = Column(String)

    tokens = relationship('Token', back_populates='power_plant', lazy='dynamic')

    mix = relationship('Mix',
                       back_populates='power_plant',
                       lazy='dynamic')

    def __repr__(self):
        return '<PowerPlant id=%s (%s)>' % (self.id, self.name)


class Biomass(Base):
    __tablename__ = BIOMASS_TABLENAME

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    mixes = relationship('Mix', back_populates='biomass')


class Mix(Base):
    __tablename__ = MIX_TABLENAME
    __table_args__ = (UniqueConstraint('power_plant_id', 'biomass_id'),)

    id = Column(Integer, primary_key=True)

    power_plant_id = Column(Integer, ForeignKey('%s.id' % POWER_PLANT_TABLENAME))
    power_plant = relationship('PowerPlant', back_populates='mix')

    biomass_id = Column(Integer, ForeignKey('%s.id' % BIOMASS_TABLENAME))
    biomass = relationship('Biomass', back_populates='mixes')

    ratio = Column(Integer)


class Token(Base):
    __tablename__ = TOKEN_TABLENAME
    __table_args__ = (
        UniqueConstraint('contract_id', 'certificate_id'),
        Index('%s.owner_index' % TOKEN_TABLENAME, 'owner'),
        Index('%s.meta_data' % TOKEN_TABLENAME, 'meta_data'),
    )

    id = Column(Integer, primary_key=True)

    certificate_id = Column(String)

    contract_id = Column(Integer, ForeignKey('%s.id' % CONTRACT_TABLENAME))
    contract = relationship('Contract', back_populates='tokens')

    meta_data = Column(String, ForeignKey('%s.meta_data' % POWER_PLANT_TABLENAME))
    power_plant = relationship('PowerPlant', back_populates='tokens')

    owner = Column(String)

    is_claimed = Column(Boolean, default=False)
    claimer = Column(String)

    logs = relationship('Log', back_populates='token', lazy='dynamic')

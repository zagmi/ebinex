import pytest
from . import config
from ebinexpy import Ebinex

@pytest.fixture(scope='session')
def client():
    ebinex = Ebinex(config.email, config.password, keep=True)
    yield ebinex
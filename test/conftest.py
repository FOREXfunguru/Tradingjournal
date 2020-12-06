import pytest

from trade import Trade

@pytest.fixture
def t_object():
    '''Returns a Trade object'''

    td = Trade(
        start="2017-04-10 14:00:00",
        end="2017-04-26 14:00:00",
        entry=0.75308,
        TP=0.7594,
        SL=0.74889,
        pair="AUD/USD",
        type="long",
        timeframe="H8",
        strat="counter_b2",
        id="AUD_USD 10APR2017H8")
    return td
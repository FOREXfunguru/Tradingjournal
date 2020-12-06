import pytest
import os
import pdb

from trade_journal import TradeJournal
from pathlib import Path

@pytest.fixture
def tjO():
    '''Returns a trade_journal object for a Counter trade'''
    td = TradeJournal(url=os.getenv('DATADIR')+"/testCounter.xlsx",
                      worksheet="trading_journal")
    return td

@pytest.fixture
def clean_tmp():
    yield
    print("\nCleanup .xlsx file")
    os.remove(os.getenv('DATADIR')+"testCounter1.xlsx")

def test_tj_nonexists(clean_tmp):
    '''Instantiates a trade_journal object when the .xlsx pointed by url does not exist'''

    fname = Path(os.getenv('DATADIR')+"/testCounter1.xlsx")

    td = TradeJournal(url=fname,
                      worksheet="trading_journal")

    # check that fname has been initialized
    assert fname.exists() is True

def test_win_rate(tjO):

    (number_s, number_f, tot_pips) = tjO.win_rate(strats="counter")

    assert number_s == 2
    assert number_f == 1
    assert tot_pips == 274.5

def test_write_tradelist(tjO):
    trade_list = tjO.fetch_tradelist()
    trade_list.analyze()

    tjO.write_tradelist(trade_list)
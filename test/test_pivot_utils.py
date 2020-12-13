import pytest
import logging
import datetime

from trade import Trade
from pivot_utils import *
from trade_utils import *

@pytest.mark.parametrize("pair,"
                         "timeframe,"
                         "id,"
                         "start,"
                         "type,"
                         "SR,"
                         "SL,"
                         "TP,"
                         "entry,"
                         "dates",
                         [('EUR_GBP', 'D', 'EUR_GBP 28JAN2007D', '2007-01-27 22:00:00', 'long', 0.6595, 0.65376, 0.6691,
                              0.65989, [datetime.datetime(2004, 6, 9, 21, 0), datetime.datetime(2004, 8, 1, 21, 0),
                                        datetime.datetime(2005, 6, 23, 21, 0), datetime.datetime(2007, 1, 28, 22, 0)]),
                             ('EUR_GBP', 'D', 'EUR_GBP 22MAY2007D', '2007-05-21 21:00:00', 'short', 0.6833, 0.68584, 0.6771,
                              0.68235, [datetime.datetime(2003, 11, 2, 22, 0), datetime.datetime(2004, 3, 10, 22, 0),
                                        datetime.datetime(2004, 12, 16, 22, 0)]),
                             ('EUR_GBP', 'D', 'EUR_GBP 04JUN2004D', '2004-06-03 22:00:00', 'long', 0.66379, 0.66229, 0.67418,
                             0.66704, [datetime.datetime(2004, 3, 1, 22, 0)]),
                            ('EUR_JPY', 'D', 'EUR_JPY 04MAY2016D', '2016-05-03 22:00:00', 'long', 122.173, 121.57,
                             125.138, 123.021, [datetime.datetime(2009, 3, 1, 22, 0), datetime.datetime(2010, 3, 22, 21, 0),
                                                datetime.datetime(2016, 5, 4, 21, 0)]),
                            ])
def test_get_pivots(pair, id, timeframe, start, type, SR, SL, TP, entry, dates, clean_tmp):
    t = Trade(
        id=id,
        start=start,
        pair=pair,
        timeframe='D',
        type=type,
        SR=SR,
        SL=SL,
        TP=TP,
        entry=entry,
        strat='counter_b1')

    aPivotList = get_pivots(t)

    times = []
    for p in aPivotList.plist:
        times.append(p.candle['time'])

    assert dates == times

@pytest.mark.parametrize("pair,"
                         "id,"
                         "start,"
                         "type,"
                         "SR,"
                         "SL,"
                         "TP,"
                         "entry,"
                         "dates",
                         [('EUR_AUD', 'EUR_AUD 04DEC2018D', '2018-12-03 22:00:00', 'long', 1.54123, 1.53398, 1.55752, 1.54334,
                          [datetime.datetime(2018, 11, 29, 22, 0)]),
                          ('EUR_AUD', 'EUR_AUD 08MAY2017D', '2017-05-08 22:00:00', 'short', 1.48820, 1.49191, 1.46223, 1.48004,
                           [datetime.datetime(2017, 5, 7, 21, 0)]),
                           ('EUR_AUD', 'EUR_AUD 24MAY2019D', '2019-05-23 22:00:00', 'short', 1.62344, 1.62682, 1.60294, 1.61739,
                           [datetime.datetime(2015, 8, 23, 21, 0), datetime.datetime(2018, 12, 30, 22, 0),
                            datetime.datetime(2019, 5, 21, 21, 0)]),
                           ('GBP_USD', 'GBP_USD 18APR2018D', '2018-04-17 22:00:00', 'short', 1.43690, 1.43778, 1.41005, 1.42681,
                           [datetime.datetime(2018, 4, 15, 21, 0)])])
def test_get_pivots_lasttime(pair, id, start, type, SR, SL, TP, entry, dates, clean_tmp):
    """
    Test 'get_pivots_lasttime' function
    """
    t = Trade(
        id=id,
        start=start,
        pair=pair,
        timeframe='D',
        type=type,
        SR=SR,
        SL=SL,
        TP=TP,
        entry=entry,
        strat='counter_b1')

    lasttime = get_lasttime(t)
    pl = get_pivots(t)
    new_pl = get_pivots_lasttime(pl,lasttime)

    times = []
    for p in new_pl.plist:
        times.append(p.candle['time'])

    assert dates == times


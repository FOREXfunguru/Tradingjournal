# Collection of utilities used by the Trade object
import logging
import pdb
import datetime as dt

from utils import *
from harea import HArea
from config import CONFIG
from candle.candlelist_utils import *

# create logger
t_logger = logging.getLogger(__name__)
t_logger.setLevel(logging.INFO)

def is_entry_onrsi(trade):
    '''
    Function to check if tObj.start is on RSI

    Parameter
    ---------
    trade : Trade object
            Used for the calculation

    Returns
    -------
    True if tObj.start is on RSI (i.e. RSI>=70 or RSI<=30)
    False otherwise
    '''
    if trade.period.data['candles'][-1]['rsi'] >= 70 or trade.period.data['candles'][-1]['rsi'] <= 30:
        return True
    else:
        return False

def get_lasttime(trade):
        '''
        Function to calculate the last time price has been above/below
        a certain HArea

        Parameters
        ----------
        trade : Trade object
                Used for the calculation

        Returns
        -------
        Datetime
        '''
        t_logger.debug("Running get_lasttime")

        # instantiate an HArea object representing the self.SR in order to calculate the lasttime
        # price has been above/below SR
        resist = HArea(price=trade.SR,
                       pips=CONFIG.getint('harea', 'hr_pips'),
                       instrument=trade.pair,
                       granularity=trade.timeframe)

        return trade.period.get_lasttime(resist)

def get_max_min_rsi(trade):
    """
    Function to calculate the max or min RSI for CandleList slice
    going from trade.start-CONFIG.getint('counter', rsi_period') to trade.start.

    Returns
    -------
    float : The max (if short trade) or min (long trade) rsi value
            in the candlelist
    """
    t_logger.debug("Running set_max_min_rsi")

    ix = CONFIG.getint('counter', 'rsi_period')
    sub_clist = trade.period.data['candles'][-ix:]
    rsi_list = [x['rsi'] for x in sub_clist]
    first = None
    for x in reversed(rsi_list):
        if first is None:
            first = x
        elif trade.type == 'short':
            if x > first:
                first = x
        elif trade.type == 'long':
            if x < first:
                first = x

    t_logger.debug("Done set_max_min_rsi")

    return round(first, 2)

def calc_trade_session(trade):
    '''
    Function to calculate the trade session (European, Asian,
    NAmerican) the trade was taken

    Parameters
    ----------
    trade : Trade object
            Used for the calculation

    Returns
    -------
    str Comma-separated string with different sessions: i.e. european,asian
                                                        or namerican, etc...
    I will return n.a. if self.entry_time is not defined
    '''
    if not hasattr(trade, 'entry_time'):
        return "n.a."
    dtime = dt.datetime.strptime(trade.entry_time, '%Y-%m-%dT%H:%M:%S')
    # define the different sessions time boundaries
    a_u2 = dt.time(int(7), int(0), int(0))
    a_l2 = dt.time(int(0), int(0), int(0))
    a_u1 = dt.time(int(23), int(59), int(59))
    a_l1 = dt.time(int(23), int(0), int(0))
    e_u = dt.time(int(15), int(0), int(0))
    e_l = dt.time(int(7), int(0), int(0))
    na_u = dt.time(int(19), int(0), int(0))
    na_l = dt.time(int(12), int(0), int(0))

    sessions = []
    session_seen = False
    if dtime.time() >= a_l1 and dtime.time() <= a_u1:
        sessions.append('asian')
        session_seen = True
    if dtime.time() >= a_l2 and dtime.time() <= a_u2:
        sessions.append('asian')
        session_seen = True
    if dtime.time() >= e_l and dtime.time() <= e_u:
        sessions.append('european')
        session_seen = True
    if dtime.time() >= na_l and dtime.time() <= na_u:
        sessions.append('namerican')
        session_seen = True
    if session_seen is False:
        sessions.append('nosession')
    return ",".join(sessions)

def calc_pips_c_trend(trade):
    '''
    Function to calculate the pips_c_trend value.
    This value represents the average number of pips for each candle from
    trade.trend_i up to trade.start

    Parameters
    ----------
    trade : Trade object
            Used for the calculation

    Returns
    -------
    Float
    '''
    sub_cl = trade.period.slice(start=trade.trend_i,
                                end =trade.start)

    pips_c_trend = sub_cl.get_length_pips()/sub_cl.get_length_candles()

    return round(pips_c_trend, 1)

def get_trade_type(dt, clObj):
    """
    Function to get the type of a Trade (short/long)

    Parameters
    ----------
    dt : datetime object
        This will be the datetime for the IC candle
    clObj : CandleList object

    Returns
    -------
    str: type
         'short'/'long'
    """
    if dt != clObj.data['candles'][-1]['time']:
        dt = clObj.data['candles'][-1]['time']

    PL = clObj.get_pivotlist(th_bounces=0.01)

    # now, get the Pivot matching the datetime for the IC+1 candle
    if PL.plist[-1].candle['time'] != dt:
        raise Exception("Last pivot time does not match the passed datetime")
    # check the 'type' of Pivot.pre segment
    direction = PL.plist[-1].pre.type

    if direction == -1 :
        return 'long'
    elif direction == 1 :
        return 'short'
    else:
        raise Exception("Could not guess the file type")

def calc_adr(trade):
    """
    Function to calculate the ATR (avg timeframe rate)
    from trade.start - CONFIG.getint('trade', 'period_atr')

    Parameters
    ----------
    trade : Trade object
            Used for the calculation

    Returns
    -------
    float : ATR for selected period
    """
    delta_period = periodToDelta(CONFIG.getint('trade', 'period_atr'),
                                 trade.timeframe)
    delta_1 = periodToDelta(1, trade.timeframe)
    start = trade.start - delta_period  # get the start datetime
    end = trade.start + delta_1  # increase trade.start by one candle to include trade.start

    c_list = trade.period.slice(start, end)

    return calc_atr(c_list)
    print("h")

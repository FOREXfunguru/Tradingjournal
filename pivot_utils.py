# Collection of utilities used by the Trade object
# to calculate the Pivots related to the Trade
import matplotlib
matplotlib.use('PS')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from config import CONFIG
from candle.candle import Candle
from pivot import PivotList
from utils import periodToDelta, substract_pips2price, add_pips2price
from ast import literal_eval

import pdb
import logging

# create logger
p_logger = logging.getLogger(__name__)
p_logger.setLevel(logging.INFO)

def get_pivots_lasttime(pl, lasttime):
    '''
    Function to get a PivotList with pivots occurring after lasttime

    Parameters
    ----------
    pl : PivotList object
         Used for the calculation
    lasttime : datetime object
               Lasttime

    Returns
    -------
    PivotList object in which the 'plist' will contain only
    the pivots after lasttime
    '''

    p_logger.debug("Running get_pivots_lasttime")

    new_pl = []
    for p in pl.plist:
        if p.candle['time'] >= lasttime:
            new_pl.append(p)

    new_PLobj = PivotList(plist=new_pl,
                          clist=pl.clist,
                          slist=pl.slist)

    p_logger.debug("Done set_pivots_lasttime")

    return new_PLobj

def get_pivots(trade):
    '''
    Function to get the pivots as calculated by the Zigzag module

    Parameters
    ----------
    trade : Trade object
            Used for the calculation
    outfile : file
              .png file for output. Required

    Returns
    -------
    PivotList List of Pivots within the S/R area
    '''
    p_logger.debug("Running set_pivots")

    # get PivotList using trade.period
    pivotlist = trade.period.get_pivotlist(CONFIG.getfloat('pivots', 'th_bounces'))

    # get PivotList in area
    in_area_list = __inarea_pivots(trade, pivotlist,
                                   last_pivot=CONFIG.getboolean('pivots', 'last_pivot'))

    # calculate score for Pivots
    pl = []
    for p in in_area_list.plist:
        p.calc_score()
        pl.append(p)

    newPL = PivotList(plist=pl,
                      clist=in_area_list.clist,
                      slist=in_area_list.slist)

    if CONFIG.getboolean('pivots', 'plot') is True:
        outfile = CONFIG. \
                      get('images', 'outdir') + "/pivots/{0}.sel_pivots.png".format(trade.id.replace(' ', '_'))
        outfile_rsi = CONFIG. \
                          get('images', 'outdir') + "/pivots/{0}.final_rsi.png".format(trade.id.replace(' ', '_'))

        plot_pivots(trade=trade,
                    f_pivotlist=newPL,
                    outfile_prices=outfile,
                    outfile_rsi=outfile_rsi)

    return newPL

    p_logger.debug("Done set_pivots")

def plot_pivots(trade, f_pivotlist, outfile_prices, outfile_rsi):
    '''
    Function to plot all pivots that are in the area

    Parameters
    ----------
    trade : Trade object
            Used for the calculation
    f_pivotlist : PivotList object
    outfile_prices : filename
                     Output file for prices plot
    outfile_rsi : filename
                  Output file for rsi plot
    '''
    p_logger.debug("Running plot_pivots")

    prices = []
    rsi = []
    datetimes = []
    for c in trade.period.data['candles']:
        prices.append(c[CONFIG.get('general', 'part')])
        rsi.append(c['rsi'])
        datetimes.append(c['time'])

    # getting the fig size from settings
    figsize = literal_eval(CONFIG.get('images', 'size'))
    # massage datetimes so they can be plotted in X-axis
    x = [mdates.date2num(i) for i in datetimes]

    # plotting the rsi values
    fig_rsi = plt.figure(figsize=figsize)
    ax_rsi = plt.axes()
    ax_rsi.plot(datetimes, rsi, color="black")
    fig_rsi.savefig(outfile_rsi, format='png')

    # plotting the prices for part
    fig = plt.figure(figsize=figsize)
    ax = plt.axes()
    ax.plot(datetimes, prices, color="black")

    for p in f_pivotlist.plist:
        dt = p.candle['time']
        ix = datetimes.index(dt)
        # prepare the plot for 'pre' segment
        if p.pre is not None:
            ix_pre_s = datetimes.index(p.pre.start())
            plt.scatter(datetimes[ix_pre_s], prices[ix_pre_s], s=200, c='green', marker='v')
        # prepare the plot for 'aft' segment
        if p.aft is not None:
            ix_aft_e = datetimes.index(p.aft.end())
            plt.scatter(datetimes[ix_aft_e], prices[ix_aft_e], s=200, c='red', marker='v')
        # plot
        plt.scatter(datetimes[ix], prices[ix], s=50)

    fig.savefig(outfile_prices, format='png')

    p_logger.debug("plot_pivots Done")

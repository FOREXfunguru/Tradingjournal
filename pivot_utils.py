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

def get_score(pl):
    '''
    Function to calculate the score after adding the score
    for each individual pivot

    Parameter
    ----------
    pl : PivotList object
         Used for the calculation

    returns
    -------
    float with score
    '''

    tot_score = 0
    for p in pl.plist:
        tot_score += p.score

    return round(tot_score,1)

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

def __inarea_pivots(trade,
                    pivots,
                    last_pivot=True):
    '''
    Function to identify the candles for which price is in the area defined
    by self.SR+HRpips and self.SR-HRpips

    Parameters
    ---------
    trade : Trade object
            Used for the calculation
    pivots: PivotList with pivots
    last_pivot: Boolean
                If True, then the last pivot will be considered as it is part
                of the setup. Default: True

    Returns
    -------
    PivotList with pivots that are in the area
    '''

    p_logger.debug("Running __inarea_pivots")

    # get bounces in the horizontal SR area
    lower = substract_pips2price(trade.pair,
                                 trade.SR,
                                 CONFIG.getint('pivots',
                                               'hr_pips'))
    upper = add_pips2price(trade.pair,
                           trade.SR,
                           CONFIG.getint('pivots',
                                         'hr_pips'))

    p_logger.warn("SR U-limit: {0}; L-limit: {1}".format(round(upper, 4), round(lower, 4)))

    pl = []
    for p in pivots.plist:
        # always consider the last pivot in bounces.plist as in_area as this part of the entry setup
        if pivots.plist[-1].candle['time'] == p.candle['time'] and last_pivot is True:
            adj_t = p.adjust_pivottime(clistO=pivots.clist)
            # get new CandleList with new adjusted time for the end
            newclist = pivots.clist.slice(start=pivots.clist.clist[0].time,
                                          end=adj_t)
            newp = newclist.get_pivotlist(self.settings.getfloat('pivots', 'th_bounces')).plist[-1]
            if self.settings.getboolean('counter', 'runmerge_pre') is True and newp.pre is not None:
                newp.merge_pre(slist=pivots.slist,
                               n_candles=CONFIG.getint('pivots', 'n_candles'),
                               diff_th=CONFIG.getint('pivots', 'diff_th'))
            if self.settings.getboolean('counter', 'runmerge_aft') is True and newp.aft is not None:
                newp.merge_aft(slist=pivots.slist,
                               n_candles=self.settings.getint('pivots', 'n_candles'),
                               diff_th=self.settings.getint('pivots', 'diff_th'))
            pl.append(newp)
        else:
            part_list = ['close{0}'.format(CONFIG.get('general', 'bit'))]
            if p.type == 1:
                part_list.append('high{0}'.format(CONFIG.get('general', 'bit')))
            elif p.type == -1:
                part_list.append('low{0}'.format(CONFIG.get('general', 'bit')))

            # initialize candle features to be sure that midAsk or midBid are
            # initialized
            cObj = Candle(dict_data=p.candle)
            cObj.set_candle_features()
            p.candle = cObj.__dict__
            for part in part_list:
                price = p.candle[part]
                # only consider pivots in the area
                if price >= lower and price <= upper:
                    # check if this pivot already exists in pl
                    p_seen = False
                    for op in pl:
                        if op.candle['time'] == p.candle['time']:
                            p_seen = True
                    if p_seen is False:
                        p_logger.debug("Pivot {0} identified in area".format(p.candle['time']))
                        if CONFIG.getboolean('counter', 'runmerge_pre') is True and p.pre is not None:
                            p.merge_pre(slist=pivots.slist,
                                        n_candles=CONFIG.getint('pivots', 'n_candles'),
                                        diff_th=CONFIG.getint('pivots', 'diff_th'))
                        if CONFIG.getboolean('counter', 'runmerge_aft') is True and p.aft is not None:
                            p.merge_aft(slist=pivots.slist,
                                        n_candles=CONFIG.getint('pivots', 'n_candles'),
                                        diff_th=CONFIG.getint('pivots', 'diff_th'))
                        pl.append(p)

    p_logger.debug("Done __inarea_pivots")
    return PivotList(plist=pl,
                     clist=pivots.clist,
                     slist=pivots.slist)
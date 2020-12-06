from pattern.counter import Counter

import pdb
import logging
import datetime
import math

# create logger
tl_logger = logging.getLogger(__name__)
tl_logger.setLevel(logging.DEBUG)

class TradeList(object):
    '''
    Class that represents a list of Trade objects

    Class variables
    ---------------
    tlist : list, Required
            List of Trade objects
    '''

    def __init__(self, tlist):
        self.tlist = tlist

    def analyze(self):
        '''
        Analyze each of the Trade objects in TradeList depending
        on value of settings.get('counter', 'strats') and add the
        calculated attributes to Trade

        :returns
        TradeList
        '''
        #these are the strategies that will be analysed using the Counter pattern
        tl_logger.info("Strategies that will be analysed: {0}".format(self.settings.get('counter', 'strats')))
        strats = self.settings.get('counter', 'strats').split(",")
        trade_list = []
        for t in self.tlist:
            tl_logger.info("Processing trade: {0}-{1}".format(t.pair, t.start))
            if t.strat in strats:
                if t.entered is False and (not hasattr(t, 'outcome') or math.isnan(t.outcome) is True):
                    t.run_trade()
                c = Counter(trade=t,
                            settingf=self.settingf,
                            settings=self.settings,
                            ser_data_obj=self.ser_data_obj,
                            init_feats=True)
                tl_logger.debug("Counter attributes analysed:{0}".format(self.settings.get('counter', 'attrbs').split(",")))
                attrb_ls = self.settings.get('counter', 'attrbs').split(",")
                for a in attrb_ls:
                    if hasattr(c, a) is True:
                        # add 'a' attribute to Trade object
                        setattr(t, a, getattr(c, a))
                    else:
                        tl_logger.warn("Attribute {0} is not defined in Counter object. Skipping...".format(a))
                        setattr(t, a, "n.a.")
            else:
                tl_logger.debug("Trade.strat ({0}) is not within list of trades to analyse. Skipping...".format(t.strat))
            trade_list.append(t)
            tl_logger.info("Done")
        tl = TradeList(settingf=self.settingf,
                       settings=self.settings,
                       tlist=trade_list)

        return tl






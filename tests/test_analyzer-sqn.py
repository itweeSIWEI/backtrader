#!/usr/bin/env python
# 编码:utf-8;py-indent-offset: 4 - *
# ###############################################################################
# #
# 版权所有(C) Daniel Rodriguez 2015-2023
# #
# 这个程序是免费的软件:你可以重新分配它或修改它
# 这是按照《角马将军公共许可证》的规定
# 自由软件基金会，两种版本的许可证
# (在你选择的时候)任何后期版本。
# #
# /这个项目是在希望有用的情况下分发的，
# 但是没有任何WARRANTY;甚至没有隐含的警告
# 参与目的的商品或健身。看清
# GNU将军对细节的许可证。
# #
# 你应该收到一份《角马将军执照》的复印件
# 按照这个计划。如果你不知道，看看<http://www.gnu.org/licenses/>。
# #
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import time

try:
    # 系统的当前时间和用户CPU时间的浮动值(以秒为单位)
    time_clock = time.process_time
except:
    # 统计cpu时间的工具，这在统计某一程序或函数的执行速度最为合适。两次调用time.clock()函数的插值即为程序运行的cpu时间。
    time_clock = time.clock

import testcommon

import backtrader as bt
import backtrader.indicators as btind


# 测试策略
class TestStrategy(bt.Strategy):
    params = (
        ('period', 15),
        ('maxtrades', None),
        ('printdata', True),
        ('printops', True),
        ('stocklike', True),
    )

    def log(self, txt, dt=None, nodate=False):
        if not nodate:
            dt = dt or self.data.datetime[0]
            dt = bt.num2date(dt)
            print('%s, %s' % (dt.isoformat(), txt))
        else:
            print('---------- %s' % (txt))

    def notify_trade(self, trade):
        if trade.isclosed:
            self.tradecount += 1

    def notify_order(self, order):
        if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
            return  # Await further notifications

        if order.status == order.Completed:
            if isinstance(order, bt.BuyOrder):
                if self.p.printops:
                    txt = 'BUY, %.2f' % order.executed.price
                    self.log(txt, order.executed.dt)
                chkprice = '%.2f' % order.executed.price
                self.buyexec.append(chkprice)
            else:  # elif isinstance(order, SellOrder):
                if self.p.printops:
                    txt = 'SELL, %.2f' % order.executed.price
                    self.log(txt, order.executed.dt)

                chkprice = '%.2f' % order.executed.price
                self.sellexec.append(chkprice)

        elif order.status in [order.Expired, order.Canceled, order.Margin]:
            if self.p.printops:
                self.log('%s ,' % order.Status[order.status])

        # Allow new orders
        self.orderid = None

    def __init__(self):
        # Flag to allow new orders in the system or not
        self.orderid = None

        self.sma = btind.SMA(self.data, period=self.p.period)
        self.cross = btind.CrossOver(self.data.close, self.sma, plot=True)

    def start(self):
        if not self.p.stocklike:
            self.broker.setcommission(commission=2.0, mult=10.0, margin=1000.0)

        if self.p.printdata:
            self.log('-------------------------', nodate=True)
            self.log('Starting portfolio value: %.2f' % self.broker.getvalue(),
                     nodate=True)

        self.tstart = time_clock()

        self.buycreate = list()
        self.sellcreate = list()
        self.buyexec = list()
        self.sellexec = list()
        self.tradecount = 0

    def stop(self):
        tused = time_clock() - self.tstart
        if self.p.printdata:
            self.log('Time used: %s' % str(tused))
            self.log('Final portfolio value: %.2f' % self.broker.getvalue())
            self.log('Final cash value: %.2f' % self.broker.getcash())
            self.log('-------------------------')
        else:
            pass

    def next(self):
        if self.p.printdata:
            self.log(
                'Open, High, Low, Close, %.2f, %.2f, %.2f, %.2f, Sma, %f' %
                (self.data.open[0], self.data.high[0],
                 self.data.low[0], self.data.close[0],
                 self.sma[0]))
            self.log('Close %.2f - Sma %.2f' %
                     (self.data.close[0], self.sma[0]))

        if self.orderid:
            # if an order is active, no new orders are allowed
            return

        if not self.position.size:
            if self.p.maxtrades is None or self.tradecount < self.p.maxtrades:
                if self.cross > 0.0:
                    if self.p.printops:
                        self.log('BUY CREATE , %.2f' % self.data.close[0])

                    self.orderid = self.buy()
                    chkprice = '%.2f' % self.data.close[0]
                    self.buycreate.append(chkprice)

        elif self.cross < 0.0:
            if self.p.printops:
                self.log('SELL CREATE , %.2f' % self.data.close[0])

            self.orderid = self.close()
            chkprice = '%.2f' % self.data.close[0]
            self.sellcreate.append(chkprice)


chkdatas = 1


def test_run(main=False):
    datas = [testcommon.getdata(i) for i in range(chkdatas)]

    for maxtrades in [None, 0, 1]:
        cerebros = testcommon.runtest(datas,
                                      TestStrategy,
                                      printdata=main,
                                      stocklike=False,
                                      maxtrades=maxtrades,
                                      printops=main,
                                      plot=main,
                                      analyzer=(bt.analyzers.SQN, {}))

        for cerebro in cerebros:
            strat = cerebro.runstrats[0][0]  # no optimization, only 1
            analyzer = strat.analyzers[0]  # only 1
            analysis = analyzer.get_analysis()
            if main:
                print(analysis)
                print(str(analysis.sqn))
            else:
                if maxtrades == 0 or maxtrades == 1:
                    assert analysis.sqn == 0
                    assert analysis.trades == maxtrades
                else:
                    # Handle different precision
                    assert str(analysis.sqn)[0:14] == '0.912550316439'
                    assert str(analysis.trades) == '11'


if __name__ == '__main__':
    test_run(main=True)

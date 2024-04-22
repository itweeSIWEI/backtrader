import os.path
import sys
import datetime  # 时间参数

import backtrader as bt


# 马丁策略 版本1
class ImprovedMartingaleStrategy(bt.Strategy):
    params = (
        ('initial_stake', 10),
        ('multiplier', 2),
        ('printlog', True),
    )

    def log(self, txt, dt=None, doprint=False):
        """ 日志函数，用于记录交易执行情况 """
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()}, {txt}')

    def __init__(self):
        self.order = None
        self.stake = self.params.initial_stake
        self.buyprice = None
        self.buycomm = None
        self.bar_executed = 0

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm {order.executed.comm:.2f}')
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # 卖出
                self.log(
                    f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm {order.executed.comm:.2f}')

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):
        if self.order:
            return

        # 检查是否持仓
        if not self.position:
            # 没有持仓，则买入
            if self.data.close[-1] < self.data.close[-2]:  # 如果价格下跌，则假设为买入信号
                self.log(f'BUY CREATE, {self.data.close[0]:.2f}')
                self.order = self.buy(size=self.stake)
        else:
            # 持仓已超过5天或当前价格高于买入价
            if (len(self) - self.bar_executed > 5) or (self.data.close[0] > self.buyprice * 1.05):
                self.log(f'SELL CREATE, {self.data.close[0]:.2f}')
                self.order = self.sell(size=self.position.size)
                self.stake = self.params.initial_stake  # 重置投资额
            elif self.data.close[0] < self.buyprice * 0.95:  # 如果当前价格低于买入价格的95%
                self.stake *= self.params.multiplier  # 加倍投入
                self.log(f'DOUBLING STAKE to {self.stake}')
                self.order = self.buy(size=self.stake)


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(ImprovedMartingaleStrategy, printlog=True)
    # 获取当前脚本所在目录
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # 拼接数据加载路径
    datapath = os.path.join(modpath, '../datas/orcl-1995-2014.txt')
    # 创建数据源
    data = bt.feeds.YahooFinanceCSVData(dataname=datapath,
                                        # 数据必须大于fromdate
                                        fromdate=datetime.datetime(2000, 1, 1),
                                        # 数据必须小于todate
                                        todate=datetime.datetime(2000, 12, 1),
                                        # Yahoo的价格数据有点非主流，它是以时间倒序排列的。datetime.datetime()中的reversed=True参数是将顺序反转一次
                                        reversed=False
                                        )
    cerebro.adddata(data)

    cerebro.broker.setcash(1000.0)
    cerebro.broker.setcommission(commission=0.001)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
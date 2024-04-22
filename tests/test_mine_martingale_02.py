import os.path
import sys

import backtrader as bt
import datetime  # 时间参数


# 马丁策略 版本2
class MartingaleStrategy(bt.Strategy):
    params = (
        ('initial_size', 10),  # 初始投资数量
        ('multiplier', 2),  # 加码倍数
    )

    def log(self, txt, dt=None):
        """ 日志函数，用于记录交易执行情况 """
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')

    def __init__(self):
        """ 策略初始化，可以在此处定义指标等 """
        self.order = None
        self.buy_size = self.params.initial_size
        self.buy_count = 0

    def notify_order(self, order):
        """ 订单通知，处理订单状态变化 """
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'BUY EXECUTED, Size: {order.executed.size}, Price: {order.executed.price}, Cost: {order.executed.value}')
            elif order.issell():
                self.log(
                    f'SELL EXECUTED, Size: {order.executed.size}, Price: {order.executed.price}, Cost: {order.executed.value}')
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None

    def next(self):
        """ 主逻辑执行部分，每个时间点调用 """
        if self.order:
            return  # 如果有未完成的订单，则不执行新的操作

        if not self.position:  # 如果当前没有持仓
            self.log(f'Start buy, Size: {self.buy_size}')
            self.order = self.buy(size=self.buy_size)
        else:
            if self.data.close[0] < self.data.close[-1]:
                # 如果当前价格低于上一个价格，则视为亏损，执行加码策略
                self.buy_size *= self.params.multiplier
                self.buy_count += 1
                self.log(f'Loss detected, doubling size to: {self.buy_size}')
                self.order = self.buy(size=self.buy_size)
            else:
                # 如果当前价格高于上一个价格，则视为盈利，平仓并重置投资规模
                self.log('Profit detected, closing position')
                self.close()
                self.buy_size = self.params.initial_size
                self.buy_count = 0


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MartingaleStrategy)

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

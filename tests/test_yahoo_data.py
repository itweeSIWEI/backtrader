from datetime import datetime

import backtrader as bt


class MAcrossover(bt.Strategy):  # 定义交易策略类
    def __init__(self):
        ma_fast = bt.indicators.SMA(period=10)  # 快速移动平均线
        ma_slow = bt.indicators.SMA(period=30)  # 慢速移动平均线
        self.crossover = bt.indicators.CrossOver(ma_fast, ma_slow)  # 交叉信号

    def next(self):
        if self.crossover > 0:  # 如果快速移动平均线刚好从下方穿过慢速线
            self.buy()  # 执行买入
        elif self.crossover < 0:  # 如果快速移动平均线刚好从上方穿过慢速线
            self.sell()  # 执行卖出


if __name__ == '__main__':
    cerebro = bt.Cerebro()  # 创建 Cerebro 对象
    cerebro.addstrategy(MAcrossover)  # 添加策略类
    data = bt.feeds.YahooFinanceData(dataname='AAPL', fromdate=datetime(2011, 1, 1),
                                     todate=datetime(2012, 12, 31))  # 加载数据
    cerebro.adddata(data)  # 添加数据
    cerebro.run()  # 运行
    cerebro.plot()  # 绘图

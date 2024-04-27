import backtrader as bt  # 导入backtrader框架
import datetime  # 时间参数
import sys   # 获取当前运行脚本的路径 (in argv[0])
import os.path   # 路径管理


class TestStrategy(bt.Strategy):
    params = (
        # 持仓够5个单位就卖出
        ('exitbars', 5),
        # 均线参数设置15天，15日均线
        ('maperiod', 15),
    )
    def log(self, txt, dt=None):
        # 记录策略执行的日志
        dt = dt or self.datas[0].datetime.date(0)
        print('%s,%s' % (dt.isoformat(), txt))

    def __init__(self):
        # 保存收盘价格的引用
        self.dataclose = self.datas[0].close
        # 跟踪挂单
        self.order = None
        # 买入价格和手续费
        self.buyprice = None
        self.buycomm = None
        # 加入均线指标
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maperiod)
        # 绘制图形时候用到的指标
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        bt.indicators.WeightedMovingAverage(self.datas[0], period=25, subplot=True)
        bt.indicators.StochasticSlow(self.datas[0])
        bt.indicators.MACDHisto(self.datas[0])
        rsi = bt.indicators.RSI(self.datas[0])
        bt.indicators.SmoothedMovingAverage(rsi, period=10)
        bt.indicators.ATR(self.datas[0], plot=False)

        # 执行卖出
    def notify_order(self, order):
        if order.status in [order.Submitted,order.Accepted]:
            # broke 提交了买/卖订单，则什么都不做
            return
        # 检查一个订单是否完成
        # 注意: 当资金不足时，broker会拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('已买入,价格:%.2f, 费用:%.2f, 佣金:%.2f' % (order.executed.price, order.executed.value, order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                self.log('已卖出,价格:%.2f, 费用:%.2f, 佣金:%.2f' % (order.executed.price, order.executed.value, order.executed.comm))
            # 记录当前交易数量
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('取消/保证金不足/拒绝')

        # 无挂起订单
        self.order = None

    # 交易状态通知,买卖均算交易
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('交易利润,毛利润 %.2f, 净利润 %.2f' % (trade.pnl, trade.pnlcomm))

    def next(self):
        # 记录收盘价格
        self.log('Close,%.2f' % self.dataclose[0])

        if self.order:
            # 如果有订单挂起 则不操作
            return

        # 如果没有持仓，则买入
        if not self.position:
            # 今日收盘价 < 昨日收盘价
            if self.dataclose[0] < self.dataclose[-1]:
                # 昨日收盘价 < 前日收盘价
                if self.dataclose[-1] < self.dataclose[-2]:
                    # 买入
                    self.log('买入单,%.2f' % self.dataclose[0])
                    # 跟踪订单，防止重复买入
                    self.order = self.buy()

        else:
            if len(self) >= (self.bar_executed + self.params.exitbars):
                # 全部卖出
                self.log('卖出单,%.2f' % self.dataclose[0])
                # 跟踪订单，避免重复
                self.order = self.sell()


# 创建cerebro引擎
cerebro = bt.Cerebro()
# Cerebro引擎在后台创建broke经纪人，系统默认资金是10000
# 为Cerebro引擎添加执行策略
cerebro.addstrategy(TestStrategy)
# 获取当前脚本所在目录
modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
# 拼接数据加载路径
datapath = os.path.join(modpath, '../datas/orcl-1995-2014.txt')
# 创建交易数据集
data = bt.feeds.YahooFinanceCSVData(dataname=datapath,
                                    # 数据必须大于fromdate
                                    fromdate=datetime.datetime(2000, 1, 1),
                                    # 数据必须小于todate
                                    todate=datetime.datetime(2000, 12, 1),
                                    # Yahoo的价格数据有点非主流，它是以时间倒序排列的。datetime.datetime()中的reversed=True参数是将顺序反转一次
                                    reversed=False
                                    )
# 加载交易数据
cerebro.adddata(data)
# 设置投资金额100000.0
cerebro.broker.setcash(100000.0)
# 每笔交易使用固定交易量
cerebro.addsizer(bt.sizers.FixedSize, stake=10)
# 设置佣金0.001,除以100去掉百分号
cerebro.broker.setcommission(commission=0.001)
# 引擎运行前打印资金
print('组合期初资金 %s' % cerebro.broker.getvalue())
# 运行策略
cerebro.run()
# 引擎运行后打印期末资金
print('组合期末资金 %s' % cerebro.broker.getvalue())
# 绘制图表
cerebro.plot()

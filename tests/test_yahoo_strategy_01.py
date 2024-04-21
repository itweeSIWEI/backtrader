import backtrader as bt  # 导入backtrader框架
import datetime  # 时间参数
import sys   # 获取当前运行脚本的路径 (in argv[0])
import os.path   # 路径管理


class TestStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        # 记录策略执行的日志
        dt = dt or self.datas[0].datetime.date(0)
        print('%s,%s' % (dt.isoformat(), txt))

    def __init__(self):
        # 保存收盘价格的引用
        self.dataclose = self.datas[0].close

    def next(self):
        # 记录收盘价格
        self.log('Close,%.2f' % self.dataclose[0])


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
# 引擎运行前打印资金
print('组合期初资金 %s' % cerebro.broker.getvalue())
# 运行策略
cerebro.run()
# 引擎运行后打印期末资金
print('组合期末资金 %s' % cerebro.broker.getvalue())

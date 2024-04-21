import pandas as pd
from sqlalchemy import create_engine

# 导入日数据
# CSV 文件路径
csv_file_path = './csv/AAPL_1y_1mo.csv'

# 读取 CSV 文件到 DataFrame，确保日期格式正确
df = pd.read_csv(csv_file_path)

# 日期格式使用 yyyy-MM-dd
df['Date'] = pd.to_datetime(df['Date'])  # 转换日期格式

# 时间格式使用 yyyy-MM-dd HH:mm:ss
# df.rename(columns={'Datetime': 'datetime'}, inplace=True)
# df['datetime'] = pd.to_datetime(df['datetime']).dt.tz_localize(None)

# 添加 'type' 和 'timeframe' 列
df['type'] = 'stock'  # 假定这些都是股票数据
df['ticker'] = 'AAPL'  # 股票名称
df['timeframe'] = 'month'  # 设置时间框架为 'minute', 'hour', 'day', 'week', 'month', 'year'

# 重命名列以匹配数据库字段
df.rename(columns={
    'Date': 'datetime',
    'Open': 'open',
    'High': 'high',
    'Low': 'low',
    'Close': 'close',
    'Volume': 'volume'
}, inplace=True)

# 删除不需要的 'Adj Close' 列
df.drop('Adj Close', axis=1, inplace=True)

# 创建数据库连接引擎
engine = create_engine('mysql+mysqlconnector://root:WswSecretPw@124.221.197.48:3306/backtrader')

# 将数据导入 MySQL
df.to_sql('financial_data', con=engine, index=False, if_exists='append', chunksize=500)

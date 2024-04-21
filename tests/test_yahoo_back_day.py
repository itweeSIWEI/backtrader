# import yfinance as yf
#
# # 定义股票代码和获取数据的时间范围
# ticker = 'AAPL'
# start_date = '2020-01-01'
# end_date = '2020-12-31'
#
# # 使用 yfinance 获取数据
# data = yf.download(ticker, start=start_date, end=end_date)
#
# # 保存数据到 CSV 文件
# csv_file_path = 'AAPL_2020.csv'
# data.to_csv(csv_file_path)

import yfinance as yf

# 定义股票代码和时间框架列表
ticker = 'AAPL'
timeframes = {
    '1m': '1m',  # 1分钟数据
    '1h': '1h',  # 1小时数据
    '1d': '1d',  # 1天数据
    '1wk': '1wk',  # 1周数据
    '1mo': '1mo',  # 1月数据
    '1y': '1y'  # 1年数据 (这通常是通过聚合更短的时间框架来获取)
}

# 遍历不同的时间框架
for tf_key, tf_value in timeframes.items():
    # 使用 yfinance 下载7天的数据,7d可以替换
    data = yf.download(ticker, period="7d", interval=tf_value)
    # data = yf.download(ticker, start="2020-01-01", end="2020-12-31", interval=tf_value)

    # 生成 CSV 文件路径
    csv_file_path = f'./csv/{ticker}_1y_{tf_key}.csv'

    # 保存数据到 CSV 文件
    data.to_csv(csv_file_path)
    print(f'Saved {csv_file_path}')

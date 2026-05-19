import glob
import sqlite3
import pandas as pd 

# 批量读取合并解压后的CSV文件
csv_files = glob.glob("citibike_data/*.csv")
# 补充缺失的赋值符号
df_list = [pd.read_csv(f) for f in csv_files] 
# 补充缺失的赋值符号
df_raw = pd.concat(df_list, ignore_index=True) 

print(f"原始数据总行数: {len(df_raw)}") 

# 数据清洗
df = df_raw.copy() # 补充缺失的赋值符号

# 删除关键字段为空的行(如经纬度、站点名为空)
df.dropna(subset=['start_station_name', 'end_station_name', 'end_lat', 'end_lng'], inplace=True)

# 转换时间格式为 datetime 类型,方便后续计算和分析
df['started_at'] = pd.to_datetime(df['started_at'])
df['ended_at'] = pd.to_datetime(df['ended_at'])

# 计算骑行时长(分钟)
# 补充缺失的减号运算符
df['duration_min'] = (df['ended_at'] - df['started_at']).dt.total_seconds() / 60 

# 剔除异常值:时长小于1分钟(可能是坏车秒还)或大于1440分钟(24小时,未归还)
# 修复 PDF 中的格式识别错误
df = df[(df['duration_min'] >= 1) & (df['duration_min'] <= 1440)] 

# 提取时间特征用于后续分析
df['hour'] = df['started_at'].dt.hour # 补充缺失的赋值符号
df['weekday'] = df['started_at'].dt.dayofweek # 0=周一, 6=周日
df['month'] = df['started_at'].dt.month # 

# 数据管理:存入SQLite 数据库,方便后续 SQL 查询和节约内存
conn = sqlite3.connect('citibike.db')

# 为了避免数据库过大,存入清洗后的核心字段
cols_to_save = ['rideable_type', 'started_at', 'duration_min', 'start_station_name', 'end_station_name', 'member_casual', 'hour', 'weekday']
df[cols_to_save].to_sql('trips', conn, if_exists='replace', index=False)

conn.close()
print(f"数据清洗完毕,剩余有效行数: {len(df)},已持久化至 citibike.db")
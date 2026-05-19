import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os
import numpy as np

# 忽略部分由于版本更新导致的常规警告
warnings.filterwarnings('ignore')

# ==========================================
# 0. 创建图片保存目录
# ==========================================
output_dir = 'res_imgs'
os.makedirs(output_dir, exist_ok=True)

# ==========================================
# 1. 本地环境中文显示设置
# ==========================================
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False 

# ==========================================
# 2. 从数据库加载数据
# ==========================================
print("正在从数据库加载数据...")
conn = sqlite3.connect('citibike.db')
df = pd.read_sql_query("SELECT * FROM trips", conn, parse_dates=['started_at'])
conn.close()

df['month'] = df['started_at'].dt.month

print(f"数据加载完成，共 {len(df)} 条记录。开始生成分析图表...")

# ==========================================
# 3. 数据可视化 (多样化图表组合)
# ==========================================

# ------------------------------------------
# RQ1: 一天(24小时)和一周(工作日 vs 周末)的潮汐规律
# ------------------------------------------
# 图 1-1 (折线图): 24小时骑行量分布
plt.figure(figsize=(10, 5))
hourly_counts = df['hour'].value_counts().sort_index()
sns.lineplot(x=hourly_counts.index, y=hourly_counts.values, marker='o', color='b', linewidth=2)
plt.title('RQ1_图1: 24小时骑行量分布特征 (早晚高峰折线图)')
plt.xlabel('小时 (0-23)')
plt.ylabel('总骑行次数')
plt.xticks(range(0, 24))
plt.savefig(os.path.join(output_dir, 'RQ1_fig1_hourly_line.png'), dpi=300, bbox_inches='tight')
plt.close()

# 图 1-2: 星期 vs 小时 交叉热力图 (Heatmap)
plt.figure(figsize=(12, 6))
# 透视表：计算每一天每一个小时的骑行次数
heatmap_data = df.pivot_table(index='weekday', columns='hour', values='duration_min', aggfunc='count')
# 将数字索引替换为中文星期
heatmap_data.index = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
sns.heatmap(heatmap_data, cmap='YlGnBu', linewidths=.5)
plt.title('RQ1_图2: 星期与小时骑行量交叉热力图 (精准定位潮汐时刻)')
plt.xlabel('小时 (0-23)')
plt.ylabel('星期')
plt.savefig(os.path.join(output_dir, 'RQ1_fig2_weekday_hour_heatmap.png'), dpi=300, bbox_inches='tight')
plt.close()

# ------------------------------------------
# RQ2: 不同用户群体(Subscriber vs Customer)的差异
# ------------------------------------------
# 图 2-1 (饼图): 用户类型占比
plt.figure(figsize=(6, 6))
user_counts = df['member_casual'].value_counts()
plt.pie(user_counts, labels=list(user_counts.index.astype(str)), autopct='%1.1f%%', startangle=90, colors=['#ff9999', '#66b3ff'], wedgeprops={'edgecolor': 'white'})
plt.title('RQ2_图1: 用户类型占比饼图 (member vs casual)')
plt.savefig(os.path.join(output_dir, 'RQ2_fig1_user_pie.png'), dpi=300, bbox_inches='tight')
plt.close()

# 图 2-2 (小提琴图): 骑行时长分布
plt.figure(figsize=(8, 6))
# 小提琴图能同时展示箱线图的四分位数和数据的密度核估计
sns.violinplot(x='member_casual', y='duration_min', hue='member_casual', 
               data=df[df['duration_min'] <= 60], palette='Set2', legend=False, inner="quartile")
plt.title('RQ2_图2: 不同用户群体骑行时长分布密度 (小提琴图, <=60分钟)')
plt.xlabel('用户类型')
plt.ylabel('骑行时长 (分钟)')
plt.savefig(os.path.join(output_dir, 'RQ2_fig2_duration_violin.png'), dpi=300, bbox_inches='tight')
plt.close()

# ------------------------------------------
# RQ3: 城市中核心借还流量枢纽
# ------------------------------------------
# 图 3-1 (条形图): Top 10 起始站点
plt.figure(figsize=(10, 6))
top_start_stations = df['start_station_name'].value_counts().head(10)
sns.barplot(y=top_start_stations.index, x=top_start_stations.values, hue=top_start_stations.index, palette='viridis', legend=False)
plt.title('RQ3_图1: Top 10 骑行量最大的起始站点 (水平条形图)')
plt.xlabel('出发单量')
plt.ylabel('站点名称')
plt.savefig(os.path.join(output_dir, 'RQ3_fig1_top_start_bar.png'), dpi=300, bbox_inches='tight')
plt.close()

# 图 3-2 : Top 10 结束站点 棒棒糖图 (Lollipop Chart)
plt.figure(figsize=(10, 6))
# 取 Top 10 并按升序排列，这样画出来的图频数高的在最上面
top_end_stations = df['end_station_name'].value_counts().head(10).sort_values(ascending=True)
# 绘制细线
x_values = top_end_stations.to_numpy(dtype=float)
plt.hlines(y=top_end_stations.index, xmin=0, xmax=x_values, color='skyblue', linewidth=3)
# 绘制圆点
plt.plot(x_values, top_end_stations.index, "o", markersize=10, color='royalblue')
plt.title('RQ3_图2: Top 10 骑行量最大的结束站点 (棒棒糖图)')
plt.xlabel('到达单量')
plt.ylabel('站点名称')
plt.grid(axis='y', linestyle='--', alpha=0.7) # 添加水平参考线
plt.savefig(os.path.join(output_dir, 'RQ3_fig2_top_end_lollipop.png'), dpi=300, bbox_inches='tight')
plt.close()

# ------------------------------------------
# RQ4: 季节与月份交替对单量的影响
# ------------------------------------------
# 图 4-1 : 1-6月整体骑行量 堆叠面积图 (Stacked Area Chart)
plt.figure(figsize=(10, 6))
# 将数据转换为行是月份，列是用户类型，值是单量的交叉表
monthly_user_pivot = df.groupby(['month', 'member_casual']).size().unstack(fill_value=0)
months_labels = [f'{i}月' for i in monthly_user_pivot.index]

plt.stackplot(months_labels, monthly_user_pivot['member'], monthly_user_pivot['casual'], 
              labels=['member (订阅者)', 'casual (单次客)'], colors=['#ff9999', '#66b3ff'], alpha=0.8)
plt.title('RQ4_图1: 2023年上半年按用户群体划分的月度骑行量 (堆叠面积图)')
plt.xlabel('月份')
plt.ylabel('骑行总次数')
plt.legend(loc='upper left')
plt.savefig(os.path.join(output_dir, 'RQ4_fig1_monthly_stacked_area.png'), dpi=300, bbox_inches='tight')
plt.close()

# 图 4-2 : 1-6月各用户群体平均骑行时长趋势 点线图 (Point Plot)
plt.figure(figsize=(10, 6))
# 探究除了单量，温度上升是否会让大家骑得更久
# 限制异常值，只看120分钟内的均值变化规律
sns.pointplot(data=df[df['duration_min'] <= 120], x='month', y='duration_min', 
              hue='member_casual', estimator=np.mean, errorbar=None, palette='Set1', markers=['o', 's'])
plt.title('RQ4_图2: 不同用户群体的月度平均骑行时长趋势 (点线图)')
plt.xlabel('月份')
plt.ylabel('平均骑行时长 (分钟)')
plt.xticks(ticks=range(6), labels=[f'{i}月' for i in range(1, 7)])
plt.grid(axis='both', linestyle='--', alpha=0.5)
plt.savefig(os.path.join(output_dir, 'RQ4_fig2_monthly_duration_point.png'), dpi=300, bbox_inches='tight')
plt.close()

print(f"所有图表已成功生成并保存在 '{output_dir}' 文件夹下！")
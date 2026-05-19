# 🚲 Citi Bike Data Analysis

![Python Version](https://img.shields.io/badge/Python-3.10.11-blue.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)
![Pandas](https://img.shields.io/badge/Data-Pandas-150458.svg)
![Seaborn](https://img.shields.io/badge/Visualization-Seaborn-4C72B0.svg)

## 📌 项目简介 (Project Overview)

本项目基于纽约花旗单车（Citi Bike）2023年上半年（1月-6月）的开源行程数据，开展了端到端的数据分析实验。项目构建了一条完整的自动化数据流水线，涵盖了**数据自动化采集**、**数据清洗与持久化存储**以及**多维数据可视化分析**。

通过挖掘这些数据，本项目重点解答了以下四个核心研究问句（Research Questions）：
1. **时间潮汐规律**：城市单车使用量在 24 小时以及一周内的潮汐变化。
2. **用户行为差异**：长期订阅者（Member）与单次购买客（Casual）的骑行习惯对比。
3. **空间枢纽定位**：城市核心借还车流量的地理枢纽识别。
4. **气候季节影响**：月份交替与气温回升对整体单量及单次骑行时长的异质性影响。

---

## 📂 目录结构 (Directory Structure)

```text
📦 data_analysis_experiment
 ┣ 📜 main.py                  # 主调度程序 (流水线入口)
 ┣ 📜 data_collection.py       # Step 1: 自动化下载与解压数据 (含防断连与代理机制)
 ┣ 📜 data_cleaning.py         # Step 2: 数据合并、缺失值处理与 SQLite 入库
 ┣ 📜 data-visualization.py    # Step 3: 数据分析与可视化图表生成
 ┣ 📜 requirements.txt         # 项目依赖库清单
 ┣ 📜 citibike_analysis_report.md # (自动生成) 数据分析结论报告
 ┣ 📂 citibike_data/           # (自动生成) 原始 CSV 数据存储目录
 ┣ 📂 res_imgs/                # (自动生成) 数据可视化图表输出目录
 ┗ 🛢️ citibike.db              # (自动生成) 清洗后的 SQLite 数据库

```

---

## 🛠️ 环境依赖与安装 (Installation)

### 1. 运行环境

* **Python**: `3.10.11`

### 2. 安装依赖库

在项目根目录下打开终端，运行以下命令安装所需的 Python 第三方库：

```bash
pip install -r requirements.txt

```

### 3. 网络配置 (重要)

本项目在 `Step 1` 会从 AWS S3 服务器拉取共计几百 MB 的数据集。由于国内网络环境原因，直连可能会遇到 `SSLError` 或 `Connection aborted`。

* 项目内嵌了自动重试与会话保持（Keep-Alive）机制。
* **代理配置**：如果遇到持续的网络报错，请打开 `data_collection.py`，确认 `proxies` 字典中的端口号与你的本地代理软件（如 v2rayN）一致。本项目默认配置为 v2rayN 的常用 HTTP 端口 `10809`：
```python
proxies = {
    "http": "[http://127.0.0.1:10809](http://127.0.0.1:10809)",
    "https": "[http://127.0.0.1:10809](http://127.0.0.1:10809)"
}

```



---

## 🚀 运行项目 (Usage)

本项目采用模块化设计，但为了方便一键执行，请直接运行主调度脚本 `main.py`。该脚本会自动按照顺序依次调用三个子流程：

```bash
python main.py

```

### 执行流水线详情：

1. **`data_collection.py`**: 从 AWS 自动拼接 URL 并下载 2023 年 1-6 月的 `.zip` 文件，并自动解压出 `.csv` 源文件至 `citibike_data` 目录。
2. **`data_cleaning.py`**: 读取所有 CSV，剔除异常值（如时间 <1 分钟或 >24 小时的死车记录）、空值，提取时间特征（小时、星期、月份），并将有效数据存储至本地轻量级数据库 `citibike.db` 以优化内存。
3. **`data-visualization.py`**: 从数据库加载清洗后的数据，生成包含热力图、小提琴图、棒棒糖图、堆叠面积图等 8 张专业可视化图表，并保存至 `res_imgs` 目录。

---

## 📊 分析成果 (Results & Insights)

运行结束后，你可以查看 `res_imgs` 文件夹获取所有可视化图表。以下是核心分析结论的简述：

* **潮汐与通勤**：呈现典型的“双峰”特征（早 8:00，晚 17:00-18:00）。工作日潮汐现象极其明显，周末则转变为全天候分散的休闲骑行。
* **核心用户盘**：长期订阅者占比高达 74.2%，是单车生态的基本盘。他们的骑行时间极短（集中在 5-8 分钟），目标明确；而单次客则更多用于休闲游览。
* **超级交通枢纽**：PATH 地铁站（如 Grove St PATH）和大型交通客运终端展现出极其强大的“流量虹吸效应”。
* **季节刺激效应**：气温回升（1月至6月）不仅让整体骑行量翻倍，还显著拉长了单次购买客的平均骑行时长，体现了“气象条件”对休闲用户的巨大影响。

---

## 📄 许可证 (License)

本项目为学习与实验性质代码，数据源归属 [Citi Bike System Data](https://citibikenyc.com/system-data) 所有。

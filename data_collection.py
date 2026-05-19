import requests
import os
import zipfile
import urllib3
import time # 新增：用于加入缓冲延迟

# 禁用因关闭 SSL 验证而产生的控制台警告信息
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 创建数据存储目录
os.makedirs("citibike_data", exist_ok=True)

# 目标:下载2023年1月到6月的新泽西(JC)区域数据
base_url = "https://s3.amazonaws.com/tripdata/"
months = [f"20230{i}" if i < 10 else f"2023{i}" for i in range(1, 7)] 
files_to_download = [f"JC-{m}-citibike-tripdata.csv.zip" for m in months] 

# 配置请求头和代理
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Connection': 'keep-alive' # 保持连接，减少握手断开的概率
}
proxies = {
    "http": "http://127.0.0.1:10809",
    "https": "http://127.0.0.1:10809"
}

print("开始自动化下载数据集...")

# 使用 Session 对象，复用底层的 TCP 连接，能极大提高挂代理时的稳定性
session = requests.Session()
session.headers.update(headers)
session.proxies.update(proxies)
session.verify = False

for file_name in files_to_download:
    url = base_url + file_name
    save_path = os.path.join("citibike_data", file_name) 
    
    # 如果文件不存在则下载
    if not os.path.exists(save_path):
        print(f"\n正在下载: {file_name} ...")
        
        max_retries = 3 # 最大重试次数
        for attempt in range(max_retries):
            try:
                # 发起请求
                response = session.get(url, stream=True, timeout=30)
                
                # 如果 AWS 返回 404 或 403，通常代表这个月份的数据 S3 上没有，直接跳过
                if response.status_code in [403, 404]:
                    print(f"⚠️ 服务器返回 {response.status_code}，文件可能不存在于服务器端: {url}")
                    break
                    
                response.raise_for_status() 
                
                # 分块写入文件
                with open(save_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print(f"✅ {file_name} 下载成功！")
                break # 成功后跳出重试循环
                        
            except Exception as e:
                print(f"❌ 第 {attempt + 1} 次尝试下载 {file_name} 时发生网络错误: {e}")
                # 清理下载了一半的损坏文件
                if os.path.exists(save_path):
                    os.remove(save_path) 
                
                # 如果还没到最后一次重试，就等几秒再试
                if attempt < max_retries - 1:
                    print("⏳ 等待 3 秒后自动重试...")
                    time.sleep(3)
                else:
                    print(f"⚠️ 已达到最大重试次数，放弃下载 {file_name}")
        
        # 成功下载完一个文件后，让程序睡 2 秒，防止把代理节点或服务器刷崩
        time.sleep(2)

    # 如果文件存在（无论是之前下载好的，还是刚刚下载成功的），则进行解压
    if os.path.exists(save_path):
        print(f"正在解压: {file_name} ...")
        try:
            with zipfile.ZipFile(save_path, 'r') as zip_ref:
                zip_ref.extractall("citibike_data")
        except zipfile.BadZipFile:
            print(f"❌ 错误: {file_name} 不是有效的 zip 文件，可能文件损坏。")

print("\n🎉 数据采集阶段脚本执行完毕!")
import subprocess
import sys

def main():
    # 1. 收集 -> 2. 清洗 -> 3. 可视化
    scripts = [
        "data_collection.py",
        "data_cleaning.py",
        "data-visualization.py"
    ]

    print("🚀 开始执行数据分析流水线...\n")

    for script in scripts:
        print(f"========== ⏳ 正在运行: {script} ==========")
        try:
            # sys.executable 确保使用当前运行 main.py 的同一个 Python 环境
            result = subprocess.run([sys.executable, script], check=True)
            print(f"========== ✅ {script} 执行完成! ==========\n")
            
        except subprocess.CalledProcessError as e:
            # 如果某个脚本执行报错（返回码不为0），则终止后续流水线
            print(f"========== ❌ {script} 执行失败! ==========")
            print(f"错误信息或返回码: {e.returncode}")
            print("流水线已终止。")
            break
        except FileNotFoundError:
            print(f"========== ❌ 找不到文件: {script} ==========")
            print("请确保该文件与 main.py 在同一目录下。")
            break

    print("🎉 所有任务调度结束。")

if __name__ == "__main__":
    main()
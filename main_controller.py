# main_controller_file_comm.py

import subprocess
import os
import re
import time

# --- 配置区 ---
ABAQUS_EXECUTABLE = r"D:\SIMULIA\Commands\abaqus.bat"
WORKER_SCRIPT = "abaqus_worker.py" 
LOG_FILE_NAME = "worker_output.log"
# --- 配置结束 ---

worker_script_path = os.path.join(os.path.dirname(__file__), WORKER_SCRIPT)
log_file_path = os.path.join(os.path.dirname(__file__), LOG_FILE_NAME)

# --- 在启动前，删除旧的日志文件，确保干净的开始 ---
if os.path.exists(log_file_path):
    os.remove(log_file_path)

command = [
    ABAQUS_EXECUTABLE,
    "cae",
    f"noGUI={worker_script_path}"
]

print("--- 主程序开始 ---")
print(f"准备执行命令: {' '.join(f'\"{c}\"' for c in command)}")

try:
    # 【核心修改】我们不再捕获输出，因为输出在文件里
    # 我们只关心进程是否成功运行 (check=True)
    subprocess.run(
        command,
        check=True,
        timeout=1800
    )
    
    print("\n--- Abaqus Worker 进程执行完毕！---")

except subprocess.CalledProcessError as e:
    print("\n[错误] Abaqus Worker 进程返回了错误码！")
    print("这通常意味着 Worker 脚本内部发生了崩溃。请检查日志文件。")
except subprocess.TimeoutExpired:
    print("\n[错误] Abaqus 执行超时！")
except Exception as e:
    print(f"\n[错误] 发生未知异常: {e}")

finally:
    # --- 无论成功还是失败，都尝试读取日志文件 ---
    print("\n--- 开始读取 Worker 日志文件 ---")
    if os.path.exists(log_file_path):
        # 等待一秒，确保文件系统已完全写入
        time.sleep(1) 
        with open(log_file_path, 'r', encoding='utf-8') as f:
            worker_output = f.read()
        
        print("\n--- 来自 Worker 的完整日志 ---")
        print("-" * 36)
        print(worker_output)
        print("-" * 36)

        # --- 解析结果 ---
        result_value = "未找到"
        match = re.search(r"\[RESULT\]\s*(.*)", worker_output)
        if match:
            result_value = match.group(1).strip()
            print("\n========================================")
            print(f"      主程序成功提取到计算结果")
            print("========================================")
            print(f"结果内容: {result_value}")
            print("========================================")
        else:
            print("\n========================================")
            print("警告：在 Worker 日志中未找到 [RESULT] 标签。")
            print("========================================")
    else:
        print("\n[严重错误] 未找到 Worker 的日志文件！Abaqus 可能未能启动或创建文件。")

    print("\n--- 主程序结束 ---")


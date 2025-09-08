# abaqus_worker_file_comm.py

import sys
import os
from abaqus import mdb
from abaqusConstants import *
import job

# --- 0. 配置日志文件 ---
# os.getcwd() 在 noGUI 模式下能正确获取主程序所在的目录
LOG_FILE = os.path.join(os.getcwd(), 'worker_output.log')

# --- 一个简单的日志记录函数 ---
def log(message):
    """将消息追加到日志文件"""
    with open(LOG_FILE, 'a') as f:
        f.write(message + '\n')

# --- 主逻辑开始 ---
try:
    # --- 1. 清理并记录启动信息 ---
    # 覆盖写入，确保每次运行都是新的日志
    with open(LOG_FILE, 'w') as f:
        f.write("--- Worker log started. ---\n")
    
    working_dir = os.getcwd()
    log(f"Worker: Working directory is: {working_dir}")
    os.chdir(working_dir)

    # --- 2. Abaqus 建模和计算 (这是我们最终的目标代码) ---
    log("Worker: Starting model creation...")
    
    model = mdb.Model(name='BeamModel')
    sketch = model.ConstrainedSketch(name='BeamSketch', sheetSize=200.0)
    sketch.rectangle(point1=(-50, -5), point2=(50, 5))
    part = model.Part(name='BeamPart', dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
    part.BaseShell(sketch=sketch)

    log("Worker: Model creation complete.")
    log("Worker: Creating job...")

    job_name = 'BeamJob'
    my_job = mdb.Job(name=job_name, model='BeamModel', description='A simple beam job')
    
    log(f"Worker: Job '{job_name}' created. Submitting...")
    
    my_job.submit(consistencyChecking=OFF)
    my_job.waitForCompletion()
    
    log(f"Worker: Job '{job_name}' completed successfully.")

    # --- 3. 提取结果并写入日志文件 ---
    # 这里只是一个示例，实际后处理会更复杂
    # 假设我们关心的结果是某个节点的位移 U2
    # 为了测试，我们先放一个固定的模拟结果
    simulated_result_value = -0.05 
    log("Worker: Post-processing finished.")

    # --- 4. 将最终结果以特定格式写入日志文件 ---
    log(f"[RESULT] {simulated_result_value}")

except Exception as e:
    # 如果发生任何错误，将其记录到日志文件中
    error_message = f"!!! WORKER FAILED !!!\nError Type: {type(e).__name__}\nError Details: {e}"
    log(error_message)
    # 以非零状态码退出，让主程序知道出错了
    sys.exit(1)

log("--- Worker finished successfully. ---")

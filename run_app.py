import sys
import subprocess
import time
import os


def main():
    # 启动后端mcp_server.py，使用subprocess启动
    script_path = "Backend/mcp_server.py"  # 或者使用完整路径

    # 获取当前环境变量并传递给子进程
    env = os.environ.copy()

    # 启动后端服务器进程
    with open("backend.log", "w") as log_f:
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=log_f,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            env=env,
        )

    # 增加等待时间，确保后端服务已启动
    time.sleep(3)

    # 启动前端Streamlit应用
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "Frontend/app.py"], env=env
    )

    try:
        # 等待前端进程结束
        frontend_process.wait()
    except KeyboardInterrupt:
        # 如果用户中断程序，则终止后端进程
        process.terminate()
        process.wait()


if __name__ == "__main__":
    main()

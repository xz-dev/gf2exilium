import subprocess
import threading
import time
import os
import logging
import datetime
import signal
import sys
import io
import queue
from threading import Thread

# 配置日志
LOG_FILE = "springgachapon_play_all.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, 'a', 'utf-8'),
    ]
)

# 全局变量
web_process = None
stop_event = threading.Event()

def run_web_server():
    """运行网页服务"""
    global web_process
    print(f"[{datetime.datetime.now()}] 启动网页服务 springgachapon_web_add.py...")
    
    try:
        # 使用subprocess.Popen运行网页服务，将输出直接传递到控制台
        web_process = subprocess.Popen(
            ["python", "springgachapon_web_add.py"],
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True
        )
        print(f"[{datetime.datetime.now()}] 网页服务已启动，PID: {web_process.pid}")
        
        # 等待进程结束
        web_process.wait()
        print(f"[{datetime.datetime.now()}] 网页服务已停止")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] 启动网页服务失败: {e}")

def stream_reader(stream, log_func, prefix):
    """从流中读取数据并使用指定函数记录"""
    for line in iter(stream.readline, ''):
        if not line:
            break
        log_func(f"[{prefix}] {line.rstrip()}")

def run_play_all(first_run=False):
    """运行springgachapon_play_all.py，实时输出日志"""
    try:
        if first_run:
            logging.info("首次运行 springgachapon_play_all.py")
        else:
            logging.info("定时运行 springgachapon_play_all.py")
        
        # 记录开始时间
        start_time = datetime.datetime.now()
        logging.info(f"开始时间: {start_time}")
        
        # 运行脚本，启用实时输出
        process = subprocess.Popen(
            ["python", "springgachapon_play_all.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1  # 行缓冲
        )
        
        # 创建两个线程分别读取stdout和stderr
        stdout_thread = Thread(
            target=stream_reader,
            args=(process.stdout, logging.info, "输出"),
            daemon=True
        )
        stderr_thread = Thread(
            target=stream_reader,
            args=(process.stderr, logging.error, "错误"),
            daemon=True
        )
        
        # 启动线程
        stdout_thread.start()
        stderr_thread.start()
        
        # 等待进程完成
        exit_code = process.wait()
        
        # 等待线程结束
        stdout_thread.join(timeout=2)
        stderr_thread.join(timeout=2)
        
        # 关闭管道
        process.stdout.close()
        process.stderr.close()
        
        # 记录结束时间和状态
        end_time = datetime.datetime.now()
        duration = end_time - start_time
        
        if exit_code == 0:
            logging.info(f"执行完成，耗时: {duration}，退出码: {exit_code}")
        else:
            logging.error(f"执行失败，耗时: {duration}，退出码: {exit_code}")
            
    except Exception as e:
        logging.error(f"运行 springgachapon_play_all.py 时发生错误: {e}")

def scheduler_thread():
    """调度器线程，负责定时运行play_all脚本"""
    # 首次运行
    if not stop_event.is_set():
        run_play_all(first_run=True)
    
    # 计算下次运行的时间
    interval_seconds = 6 * 60 * 60  # 6小时
    
    while not stop_event.is_set():
        # 等待指定时间或直到收到停止信号
        next_run_time = datetime.datetime.now() + datetime.timedelta(seconds=interval_seconds)
        logging.info(f"下次运行时间: {next_run_time}")
        
        # 以1秒为间隔检查停止事件，更快响应停止请求
        for _ in range(interval_seconds):
            if stop_event.wait(1):
                break
        
        if stop_event.is_set():
            break
            
        # 执行定时任务
        run_play_all()

def signal_handler(sig, frame):
    """处理信号，优雅地停止程序"""
    print(f"\n[{datetime.datetime.now()}] 收到停止信号，正在停止所有服务...")
    logging.info("收到停止信号，准备终止服务")
    
    # 设置停止事件
    stop_event.set()
    
    # 终止网页服务
    if web_process:
        print(f"[{datetime.datetime.now()}] 正在停止网页服务...")
        web_process.terminate()
        try:
            web_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print(f"[{datetime.datetime.now()}] 网页服务未响应，强制终止")
            web_process.kill()
    
    print(f"[{datetime.datetime.now()}] 所有服务已停止")
    logging.info("服务已停止")
    sys.exit(0)

def main():
    """主函数"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print(f"[{datetime.datetime.now()}] GF2 Exilium 服务管理器已启动")
    print(f"[{datetime.datetime.now()}] 网页服务日志将直接输出到控制台")
    print(f"[{datetime.datetime.now()}] Play All 脚本日志将实时记录到文件: {os.path.abspath(LOG_FILE)}")
    logging.info("GF2 Exilium 服务管理器已启动")
    
    # 启动调度器线程
    scheduler = threading.Thread(target=scheduler_thread, daemon=True)
    scheduler.start()
    
    # 启动网页服务（主线程）
    run_web_server()

if __name__ == "__main__":
    main()
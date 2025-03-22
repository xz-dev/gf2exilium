import os
import subprocess
import json
import time
import argparse

def read_accounts(account_file):
    """读取账号密码文件，返回账号密码列表"""
    accounts = []
    try:
        if os.path.exists(account_file):
            with open(account_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            account_data = json.loads(line)
                            if "account" in account_data and "password" in account_data:
                                accounts.append((account_data["account"], account_data["password"], account_data.get("last_run", "")))
                        except json.JSONDecodeError:
                            print(f"跳过无效的JSON行: {line}")
    except Exception as e:
        print(f"读取账号文件失败: {e}")
    return accounts

def update_account_last_run(account_file, account, timestamp):
    """更新账号的last_run时间戳"""
    lines = []
    updated = False
    
    # 读取现有数据
    try:
        if os.path.exists(account_file):
            with open(account_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                        
                    try:
                        account_data = json.loads(line)
                        if account_data.get("account") == account:
                            account_data["last_run"] = timestamp
                            updated = True
                        lines.append(json.dumps(account_data))
                    except json.JSONDecodeError:
                        lines.append(line)  # 保持无效行不变
    except Exception as e:
        print(f"读取账号文件失败: {e}")
        return False
    
    # 写回文件
    try:
        with open(account_file, 'w') as f:
            for line in lines:
                f.write(f"{line}\n")
        return updated
    except Exception as e:
        print(f"更新账号文件失败: {e}")
        return False

def read_existing_links(share_links_file):
    """读取已有的分享链接"""
    existing_links = set()
    try:
        if os.path.exists(share_links_file):
            with open(share_links_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        existing_links.add(line)
    except Exception as e:
        print(f"读取分享链接文件失败: {e}")
    return existing_links

def save_share_link(share_links_file, link):
    """保存分享链接到文件"""
    try:
        with open(share_links_file, 'a') as f:
            f.write(f"{link}\n")
        print(f"成功保存分享链接: {link}")
    except Exception as e:
        print(f"保存分享链接失败: {e}")

def run_springgachapon(account, password):
    """运行springgachapon程序并获取输出"""
    cmd = ["python", "springgachapon.py", account, password]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    share_link = None
    task_completed = False
    
    for line in process.stdout:
        print(line.strip())  # 实时输出程序日志
        if line.startswith("分享链接:"):
            share_link = line.replace("分享链接:", "").strip()
        if "任务成功全部完成" in line:
            task_completed = True
    
    process.wait()
    return share_link, task_completed

def main():
    parser = argparse.ArgumentParser(description="GF2 Exilium Spring Gachapon Controller")
    parser.add_argument("--accounts", default="accounts.json", help="账号密码文件路径")
    parser.add_argument("--links", default="share_links.txt", help="分享链接文件路径")
    args = parser.parse_args()
    
    accounts = read_accounts(args.accounts)
    if not accounts:
        print("没有找到有效的账号信息")
        return
    
    existing_links = read_existing_links(args.links)
    
    for i, account_info in enumerate(accounts):
        account, password, last_run = account_info
        current_timestamp = int(time.time())  # Unix 时间戳
        print(f"处理账号 {i+1}/{len(accounts)}: {account} (时间戳: {current_timestamp}, 上次运行: {last_run})")
        
        share_link, task_completed = run_springgachapon(account, password)
        
        if share_link and share_link not in existing_links:
            save_share_link(args.links, share_link)
            existing_links.add(share_link)
        elif share_link:
            print(f"分享链接已存在: {share_link}")
        else:
            print("未获取到分享链接")
        
        # 如果任务已完成，记录完成时间戳
        if task_completed:
            completion_timestamp = int(time.time())
            print(f"账号 {account} 任务已完成 (完成时间戳: {completion_timestamp})")
            # 更新账号的last_run
            update_account_last_run(args.accounts, account, completion_timestamp)
        
        # 延迟一段时间再处理下一个账号
        if i < len(accounts) - 1:
            print("等待30秒后处理下一个账号...")
            time.sleep(30)

    print()
    print("开始助力任务")
    for i, account_info in enumerate(accounts):
        account, password, last_run = account_info
        print(f"账号 {i+1}/{len(accounts)}: {account}")
        cmd = ["python", "springgachapon_boost.py", account, password]
        subprocess.run(cmd)
    print("助力任务完成")

if __name__ == "__main__":
    main()
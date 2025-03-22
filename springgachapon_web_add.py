from flask import Flask, request, render_template, redirect, url_for, flash
import os
import json
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = "springgachapon_secret_key"

ACCOUNTS_FILE = "accounts.json"

def read_accounts():
    """读取账号密码文件，返回账号信息列表"""
    accounts = []
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            account_data = json.loads(line)
                            if "account" in account_data and "password" in account_data:
                                accounts.append(account_data)
                        except json.JSONDecodeError:
                            print(f"跳过无效的JSON行: {line}")
        except Exception as e:
            print(f"读取账号文件失败: {e}")
    return accounts

def save_accounts(accounts):
    """保存账号密码到文件"""
    try:
        with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
            for account_data in accounts:
                f.write(f"{json.dumps(account_data)}\n")
        return True
    except Exception as e:
        print(f"保存账号文件失败: {e}")
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        account = request.form.get('account', '').strip()
        password = request.form.get('password', '').strip()
        
        if not account or not password:
            flash('账号和密码不能为空', 'error')
        else:
            accounts = read_accounts()
            
            # 检查账号是否已存在
            account_exists = False
            for i, acc in enumerate(accounts):
                if acc["account"] == account:
                    accounts[i] = {
                        "account": account,
                        "password": password,
                        "last_run": acc.get("last_run", "")
                    }
                    account_exists = True
                    break
            
            # 如果账号不存在，添加新账号
            if not account_exists:
                accounts.append({
                    "account": account,
                    "password": password,
                    "last_run": ""
                })
            
            if save_accounts(accounts):
                flash(f'账号 {account} 已保存', 'success')
            else:
                flash('保存失败', 'error')
                
        return redirect(url_for('index'))
    
    accounts = read_accounts()
    
    # 转换时间戳为可读格式
    for account in accounts:
        if account.get("last_run"):
            try:
                timestamp = int(account["last_run"])
                account["last_run_readable"] = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            except:
                account["last_run_readable"] = "无效时间戳"
        else:
            account["last_run_readable"] = "未运行"
    
    return render_template('index.html', accounts=accounts)

@app.route('/delete/<account>', methods=['POST'])
def delete_account(account):
    accounts = read_accounts()
    
    # 查找并删除账号
    for i, acc in enumerate(accounts):
        if acc["account"] == account:
            del accounts[i]
            if save_accounts(accounts):
                flash(f'账号 {account} 已删除', 'success')
            else:
                flash('删除失败', 'error')
            break
    else:
        flash(f'账号 {account} 不存在', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    # 确保templates文件夹存在
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # 创建模板文件
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write('''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GF2 Exilium 账号管理</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .container {
            background-color: #f5f5f5;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        form {
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"],
        input[type="password"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        .btn {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 15px;
            cursor: pointer;
            border-radius: 4px;
            margin-right: 5px;
        }
        .btn-delete {
            background-color: #f44336;
            padding: 5px 10px;
            font-size: 12px;
        }
        .flash-message {
            padding: 10px;
            margin-bottom: 15px;
            border-radius: 4px;
        }
        .flash-success {
            background-color: #dff0d8;
            color: #3c763d;
        }
        .flash-error {
            background-color: #f2dede;
            color: #a94442;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
    </style>
    <script>
        // 在页面加载时转换时间戳为本地时间
        document.addEventListener('DOMContentLoaded', function() {
            // 处理所有带有时间戳的元素
            const timeElements = document.querySelectorAll('.timestamp-display');
            timeElements.forEach(el => {
                const timestamp = parseInt(el.getAttribute('data-timestamp'));
                if (timestamp) {
                    const date = new Date(timestamp * 1000); // 将Unix时间戳转换为毫秒
                    el.textContent = date.toLocaleString(); // 使用浏览器的本地设置格式化时间
                }
            });
        });
    </script>
</head>
<body>
    <div class="container">
        <h1>GF2 Exilium Spring Gachapon 自动化工具</h1>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash-message flash-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <form method="post">
            <div class="form-group">
                <label for="account">账号:</label>
                <input type="text" id="account" name="account" required>
            </div>
            
            <div class="form-group">
                <label for="password">密码:</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="btn">保存账号</button>
        </form>
        
        <h2>账号列表</h2>
        {% if accounts %}
            <table>
                <tr>
                    <th>账号</th>
                    <th>最后运行时间</th>
                    <th>操作</th>
                </tr>
                {% for account in accounts %}
                    <tr>
                        <td>{{ account.account }}</td>
                        <td>
                            {% if account.last_run %}
                                <span class="timestamp-display" data-timestamp="{{ account.last_run }}">{{ account.last_run_readable }}</span>
                            {% else %}
                                未运行
                            {% endif %}
                        </td>
                        <td>
                            <form method="post" action="{{ url_for('delete_account', account=account.account) }}">
                                <button type="submit" class="btn btn-delete">删除</button>
                            </form>
                        </td>
                    </tr>
                {% endfor %}
            </table>
        {% else %}
            <p>还没有保存的账号</p>
        {% endif %}
        
        <div style="margin-top: 40px; text-align: center; font-size: 14px; color: #666;">
            <p>开源地址: <a href="https://github.com/xz-dev/gf2exilium" target="_blank">https://github.com/xz-dev/gf2exilium</a></p>
        </div>
    </div>
</body>
</html>''')
    
    # 启动 Flask 应用
    app.run(host='0.0.0.0', port=5000, debug=True)
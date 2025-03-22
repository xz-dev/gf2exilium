FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 安装必要的系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    chromium \
    ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 只复制Python脚本和requirements.txt
COPY requirements.txt /app/

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装Playwright浏览器
RUN playwright install chromium
RUN playwright install-deps chromium

COPY *.py /app/
# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai

# 端口映射
EXPOSE 5000

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget -O /dev/null http://localhost:5000/ || exit 1

# 设置容器启动命令
ENTRYPOINT ["python", "/app/springgachapon_run.py"]
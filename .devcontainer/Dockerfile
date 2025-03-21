FROM python:3.9-slim

# 设置工作目录
WORKDIR /workspace

# 复制 requirements.txt 到容器中
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件到容器中
COPY . .

# 暴露需要的端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=app.py

# 使用官方的 Python 镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /workspace
RUN apt-get update && apt-get install -y git

# 暴露 Flask 应用需要的端口
EXPOSE 5000

# 设定默认的 Flask 环境变量（可选）
ENV FLASK_APP=app.py

# 默认启动命令
# CMD ["flask", "run", "--host=0.0.0.0"]

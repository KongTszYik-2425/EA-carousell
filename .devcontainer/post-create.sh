#!/bin/bash

set -e  # 遇到错误立即退出

# 等待 MySQL 完全启动（最多尝试60次，每次1秒）
echo "⏳ 等待 MySQL 服务启动..."
attempt=0
max_attempts=60

while ! mysqladmin ping -h db -u palk -pAdmin123 --silent; do
    attempt=$((attempt+1))
    if [ $attempt -ge $max_attempts ]; then
        echo "❌ MySQL 启动超时，请检查日志"
        docker-compose logs db
        exit 1
    fi
    sleep 1
done

echo "✅ MySQL 已就绪！"

# 进入工作目录
cd /workspace

# 初始化迁移目录（如果不存在）
if [ ! -d "migrations" ]; then
    echo "🔄 初始化数据库迁移..."
    flask db init
fi

# 生成迁移脚本（自动检测模型变化）
echo "📝 生成数据库迁移..."
flask db migrate -m "自动生成迁移"

# 应用数据库迁移
echo "⚙️ 应用数据库迁移..."
flask db upgrade


echo "🎉 数据库初始化完成！"

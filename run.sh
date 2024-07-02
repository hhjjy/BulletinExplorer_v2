#!/bin/bash
# 加载环境变量

# 獲取當前腳本的位置
script_dir=$(dirname "$0")

# 將當前腳本的位置轉換為絕對路徑
script_dir=$(cd "$script_dir" && pwd)

. ./.env

docker stop postgres-main
docker rm postgres-main

echo "SQL file path: ${script_dir}/mydb_schema.sql"

# # 创建数据目录
mkdir -p "${HOST_DIR}/main_data"

# # 运行主环境数据库容器
sudo docker run --name postgres-main \
  -e POSTGRES_DB=$POSTGRES_MAIN_DB \
  -e POSTGRES_USER=$POSTGRES_MAIN_USER \
  -e POSTGRES_PASSWORD=$POSTGRES_MAIN_PASSWORD \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -d -p $POSTGRES_MAIN_PORT:5432 \
  -v "${HOST_DIR}/main_data:/var/lib/postgresql/data" \
  -v "${script_dir}/mydb_schema.sql:/docker-entrypoint-initdb.d/mydb_schema.sql" \
  postgres

# psql -h localhost -p 65432 -U admin -d mydb

#!/bin/bash

## 擷取腳本目錄
script_dir=$(dirname "$0")

## 設定腳本路徑
script_dir=$(cd "$script_dir" && pwd)

. ./.env

docker stop postgres-main
docker rm postgres-main

echo "SQL file path: ${script_dir}/mydb_schema.sql"

## 創建資料庫目錄
mkdir -p "${HOST_DIR}/main_data"

## 執行Docker
sudo docker run --name postgres-main \
  -e POSTGRES_DB=$POSTGRES_DEV_DB \
  -e POSTGRES_USER=$POSTGRES_DEV_USER \
  -e POSTGRES_PASSWORD=$POSTGRES_DEV_PASSWORD \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -d -p $POSTGRES_DEV_PORT:5432 \
  -v "${HOST_DIR}/main_data:/var/lib/postgresql/data" \
  -v "${script_dir}/mydb_schema.sql:/docker-entrypoint-initdb.d/mydb_schema.sql" \
  postgres

## 進入資料庫的方式
# psql -h localhost -p 65432 -U admin -d mydb

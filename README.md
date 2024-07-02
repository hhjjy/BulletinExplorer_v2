docker exec -it postgres-main bash
再次运行 SQL 脚本
您可以再次尝试运行修改后的 SQL 脚本。首先，确保您已经进入容器，然后运行脚本：

bash
複製程式碼
psql -U admin -d mydb -f /docker-entrypoint-initdb.d/mydb_schema.sql
确认表格已创建
在成功执行 SQL 脚本后，检查表格是否已创建：

bash
複製程式碼
psql -h 127.0.0.1 -p 5432 -U admin -d mydb
输入密码 12345。

使用以下命令查看表格：

sql
複製程式碼
\dt
这应该显示所有表格，包括 users 和 subscription。

通过这些步骤，您应该能够解决重复创建对象的问题，并成功创建所需的表格。   


# BulletinExplorer

## Table of Contents

## Included Packages and Tools

## Additional Packages Installed

## Install

## Usage
1. build postgres docker
    $ ./run.sh
2. run main function
    

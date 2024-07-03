import json, os, requests, psycopg2, traceback, time, telegram, copy, pprint, asyncio, functools,sys
from typing import List, Dict, Any
from datetime import datetime

db_config = {
    'dbname': 'mydb',
    'user': 'admin',
    'password': '12345',
    'host': '127.0.0.1',
    'port': '5432'
}

def handle_db_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except psycopg2.DatabaseError as e:
            print(f"Database error occurred: {e}")
            raise
        except Exception as e:
            print(f"An error occurred: {e}")
            raise
    return wrapper
    
def debug_info(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 獲取函數名稱
        func_name = func.__name__
        
        # 獲取位置參數和關鍵字參數的名稱和值
        func_args = func.__code__.co_varnames[:func.__code__.co_argcount]
        params = {**dict(zip(func_args, args)), **kwargs}
        
        # 打印函數名稱和參數
        print(f"Executing function: {func_name}")
        # print("Parameters:")
        # for param_name, param_value in params.items():
        #     print(f"  {param_name} = {param_value}")
        
        # 執行函數並獲取返回值
        result = func(*args, **kwargs)
        
        # 打印返回值
        print(f"Function {func_name} returned: {result}")
        
        return result
    return wrapper
# 定義數據庫管理類
class DatabaseManager:
    def __init__(self, config: Dict[str, Any]):
        if not isinstance(config, dict):
            raise TypeError("Config should be a dictionary")
        self.config = config
        print(f"DatabaseManager Config: {self.config}")

    @handle_db_exceptions
    def _execute(self, query: str, params: tuple = None, fetch: bool = False):
        # print(f"_execute: {self.config}")  # 打印配置以檢查
        connection = psycopg2.connect(**self.config)
        cursor = connection.cursor()
        cursor.execute(query, params)
        if fetch:
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            connection.close()
            return results, columns
        connection.commit()
        cursor.close()
        connection.close()
        return None, None

    @debug_info
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        results, columns = self._execute(query, params, fetch=True)
        if results:
            return [dict(zip(columns, row)) for row in results]
        return []

    def execute_non_query(self, query: str, params: tuple = ()) -> None:
        self._execute(query, params)
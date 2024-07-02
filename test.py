import datetime
from typing import Optional
from functools import wraps
from dataclasses import dataclass

@dataclass
class Logger:
    name: str
    log_to_file: bool = False
    filename: Optional[str] = None

    def __post_init__(self):
        if self.log_to_file and not self.filename:
            raise ValueError("Filename must be provided if log_to_file is True")

    def _log(self, level: str, message: str):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] [{self.name}] [{level}] {message}"
        self._output(log_message)

    def _output(self, message: str):
        print(message)
        if self.log_to_file and self.filename:
            with open(self.filename, 'a') as f:
                f.write(message + '\n')

    def info(self, message: str):
        self._log("INFO", message)

    def warning(self, message: str):
        self._log("WARNING", message)

    def error(self, message: str):
        self._log("ERROR", message)

    def log_method(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.info(f"Calling function: {func.__name__} with args: {args} and kwargs: {kwargs}")
            try:
                result = func(*args, **kwargs)
                self.info(f"Function {func.__name__} returned: {result}")
                return result
            except Exception as e:
                self.error(f"Function {func.__name__} raised an error: {e}")
                raise
        return wrapper

# 創建 Logger 實例
LLM_logger = Logger(name="LLMLogger", log_to_file=True, filename="llm.log")
Calculator_logger = Logger(name="CalculatorLogger", log_to_file=True, filename="calculator.log")

class Calculator:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.add = self.logger.log_method(self.add)
        self.subtract = self.logger.log_method(self.subtract)

    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

class Greeter:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.greet = self.logger.log_method(self.greet)

    def greet(self, name, greeting="Hello"):
        return f"{greeting}, {name}!"

# 測試函數
if __name__ == "__main__":
    calc = Calculator(logger=Calculator_logger)
    calc.add(3, 5)
    calc.subtract(10, 4)

    greeter = Greeter(logger=LLM_logger)
    greeter.greet("Alice")
    greeter.greet("Bob", greeting="Hi")

# 測試函數
if __name__ == "__main__":
    calc = Calculator(logger=Calculator_logger)
    calc.add(3, 5)
    calc.subtract(10, 4)

    greeter = Greeter(logger=LLM_logger)
    greeter.greet("Alice")
    greeter.greet("Bob", greeting="Hi")

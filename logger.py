import os
import datetime
from collections import deque

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")


class Logger:
    def __init__(self):
        self.logs = deque(maxlen=500)
        self.log_to_file = False
        self.file_max_lines = 1000
        self.debug_mode = False
        self.log_enabled = True
        self._listeners = []
    
    def configure(self, log_to_file=None, log_max_lines=None,
                  log_file_max_lines=None, debug_mode=None, log_enabled=None):
        if log_to_file is not None:
            self.log_to_file = log_to_file
        if log_max_lines is not None:
            self.logs = deque(self.logs, maxlen=log_max_lines)
        if log_file_max_lines is not None:
            self.file_max_lines = log_file_max_lines
        if debug_mode is not None:
            self.debug_mode = debug_mode
        if log_enabled is not None:
            self.log_enabled = log_enabled
    
    def add_listener(self, callback):
        if callback not in self._listeners:
            self._listeners.append(callback)
    
    def _notify(self):
        for cb in self._listeners:
            try:
                cb()
            except:
                pass
    
    def log(self, level, message):
        # 日志总开关
        if not self.log_enabled:
            return
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] [{level}] {message}"
        self.logs.append(line)
        
        if self.log_to_file:
            try:
                os.makedirs(LOG_DIR, exist_ok=True)
                with open(LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(line + "\n")
                self._trim_log_file()
            except Exception as e:
                print(f"写入日志文件失败: {e}")
        
        self._notify()
    
    def _trim_log_file(self):
        try:
            if not os.path.exists(LOG_FILE):
                return
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if len(lines) > self.file_max_lines:
                lines = lines[-self.file_max_lines:]
                with open(LOG_FILE, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
        except Exception as e:
            print(f"修剪日志文件失败: {e}")
    
    def info(self, message):
        self.log("INFO", message)
    
    def warning(self, message):
        self.log("WARN", message)
    
    def error(self, message):
        self.log("ERROR", message)
    
    def debug(self, message):
        if self.debug_mode:
            self.log("DEBUG", message)
    
    def get_logs(self):
        return list(self.logs)
    
    def clear(self):
        self.logs.clear()
        self._notify()


logger = Logger()
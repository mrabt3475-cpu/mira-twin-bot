"""
🔧 Utils - الأدوات المساعدة
"""
import os
import json
import logging
import shutil
from datetime import datetime
from typing import Any, Dict, Optional

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """إنشاء logger"""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(getattr(logging, level.upper()))
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    os.makedirs('logs', exist_ok=True)
    file_handler = logging.FileHandler(f'logs/{name}_{datetime.now().strftime("%Y-%m-%d")}.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger

class Database:
    """قاعدة البيانات"""
    
    def __init__(self, data_file: str = 'mira_data.json'):
        self.data_file = data_file
        self.logger = setup_logger('Database')
    
    def load(self) -> Dict[str, Any]:
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"users": {}}
    
    def save(self, data: Dict[str, Any], backup: bool = True) -> bool:
        try:
            if backup and os.path.exists(self.data_file):
                self.backup()
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"خطأ: {e}")
            return False
    
    def backup(self):
        try:
            os.makedirs('backups', exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy2(self.data_file, f"backups/{self.data_file}.{timestamp}.bak")
        except:
            pass

def format_number(num: int) -> str:
    return f"{num:,}"

def format_balance(balance: int) -> str:
    return f"💰 الرصيد: **{balance}** نقطة"

def format_level(level: int, xp: int) -> str:
    return f"📊 المستوى: **{level}** (XP: {xp})"

def is_admin(user_id: int, admin_ids: list) -> bool:
    return user_id in admin_ids
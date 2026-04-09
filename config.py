"""
⚙️ Configuration - الإعدادات
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """إعدادات البوت"""
    
    # ========== Bot ==========
    BOT_TOKEN = os.getenv('BOT_TOKEN', '')
    BOT_USERNAME = os.getenv('BOT_USERNAME', 'mira')
    ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x]
    
    # ========== API Keys ==========
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
    
    # ========== Database ==========
    DATA_FILE = os.getenv('DATA_FILE', 'mira_data.json')
    BACKUP_DIR = os.getenv('BACKUP_DIR', 'backups')
    
    # ========== Payments ==========
    TON_WALLET = os.getenv('TON_WALLET_ADDRESS', '')
    PAYMENT_MIN = float(os.getenv('PAYMENT_MIN', '0.5'))
    POINTS_PER_TON = int(os.getenv('POINTS_PER_TON', '1000'))
    
    # ========== Features ==========
    ENABLE_REFERRAL = os.getenv('ENABLE_REFERRAL', 'true').lower() == 'true'
    ENABLE_SHOP = os.getenv('ENABLE_SHOP', 'true').lower() == 'true'
    ENABLE_GAMES = os.getenv('ENABLE_GAMES', 'true').lower() == 'true'
    ENABLE_WALLET = os.getenv('ENABLE_WALLET', 'true').lower() == 'true'
    ENABLE_CANVA = os.getenv('ENABLE_CANVA', 'true').lower() == 'true'
    
    # ========== Limits ==========
    MAX_POINTS_PER_DAY = int(os.getenv('MAX_POINTS_PER_DAY', '1000'))
    MAX_REFERRALS = int(os.getenv('MAX_REFERRALS', '100'))
    MAX_DAILY_STREAK = int(os.getenv('MAX_DAILY_STREAK', '30'))
    
    # ========== Referral ==========
    REFERRAL_BONUS = int(os.getenv('REFERRAL_BONUS', '50'))
    COMMISSION_RATE = float(os.getenv('COMMISSION_RATE', '0.10'))
    
    # ========== Daily Rewards ==========
    DAILY_REWARD_BASE = int(os.getenv('DAILY_REWARD_BASE', '10'))
    DAILY_REWARD_BONUS = int(os.getenv('DAILY_REWARD_BONUS', '2'))
    DAILY_REWARD_MAX_BONUS = int(os.getenv('DAILY_REWARD_MAX_BONUS', '50'))
    
    # ========== Images ==========
    FREE_IMAGES_DAILY = int(os.getenv('FREE_IMAGES_DAILY', '5'))
    IMAGE_WATERMARK = os.getenv('IMAGE_WATERMARK', 'true').lower() == 'true'
    
    # ========== Messages ==========
    WELCOME_MESSAGE = os.getenv('WELCOME_MESSAGE', '''
مرحباً! 👋

أنا **Mira**، مساعدك الذكي.

💡 **ما الذي يمكنني فعله:**
• 🎨 إنشاء صور بالذكاء الاصطناعي
• 🎵 إنشاء موسيقى وأغاني
• 🎤 تحويل النص لصوت
• 🔍 البحث في الإنترنت
• 💰 نظام النقاط والإحالة
• 🎮 ألعاب ممتعة

استخدم الأزرار أدناه للبدء!
''')
    
    # ========== Game Settings ==========
    GUESS_NUMBER_MIN = int(os.getenv('GUESS_NUMBER_MIN', '1'))
    GUESS_NUMBER_MAX = int(os.getenv('GUESS_NUMBER_MAX', '100'))
    RPS_ROUNDS = int(os.getenv('RPS_ROUNDS', '3'))
    
    # ========== Cache ==========
    CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))
    
    # ========== Debug ==========
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


class Database:
    """إعدادات قاعدة البيانات"""
    
    @staticmethod
    def get_default_data():
        return {
            "users": {},
            "shop": {
                "items": [
                    {"id": "10_images", "name": "10 صور", "price": 30, "type": "images", "amount": 10},
                    {"id": "50_images", "name": "50 صورة", "price": 120, "type": "images", "amount": 50},
                    {"id": "100_points", "name": "100 نقطة", "price": 30, "type": "points", "amount": 100},
                    {"id": "500_points", "name": "500 نقطة", "price": 120, "type": "points", "amount": 550},
                    {"id": "1000_points", "name": "1000 نقطة", "price": 200, "type": "points", "amount": 1200},
                    {"id": "pro_month", "name": "Mira Pro - شهر", "price": 500, "type": "subscription", "duration": 30},
                    {"id": "pro_year", "name": "Mira Pro - سنة", "price": 4500, "type": "subscription", "duration": 365},
                    {"id": "custom_project", "name": "مشروع مخصص", "price": 200, "type": "project", "amount": 1},
                ]
            },
            "daily_rewards": {},
            "referrals": {},
            "commissions": {},
            "games": {},
            "transactions": {}
        }
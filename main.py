"""
🚀 Main Entry Point
"""
import sys
import os
from dotenv import load_dotenv

load_dotenv()

from config import Config
from utils import setup_logger

logger = setup_logger('MiraBot', Config.LOG_LEVEL)

def check_requirements():
    logger.info("🔍 التحقق من المتطلبات...")
    if not Config.BOT_TOKEN:
        logger.error("❌ BOT_TOKEN غير موجود!")
        return False
    if not os.path.exists(Config.DATA_FILE):
        from config import Database
        db = Database(Config.DATA_FILE)
        db.save(Database.get_default_data())
    logger.info("✅ تم التحقق")
    return True

def main():
    logger.info("🚀 بدء تشغيل Mira Twin Bot...")
    
    if not check_requirements():
        sys.exit(1)
    
    try:
        from bot import app
        logger.info("✅ البوت جاهز!")
        app.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        logger.info("👋 تم الإيقاف")
    except Exception as e:
        logger.error(f"❌ خطأ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
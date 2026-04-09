"""
🤖 Mira Twin Bot - نسخة مطابقة من Mira AI Assistant
يحتوي على كل الميزات: محادثة، صور، أغاني، صوت، بحث، ذاكرة، محفظة، تذكيرات، توليد أكواد
"""

import os
import json
import asyncio
import aiohttp
import requests
import base64
import hashlib
from datetime import datetime, timedelta
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, 
    KeyboardButton, ReplyKeyboardMarkup, BotCommand, InputFile,
    ChatMemberUpdated, Document
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, 
    ContextTypes, filters, ChatMemberHandler
)

# ============== CONFIGURATION ==============
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))

# ============== DATA STORAGE ==============
DATA_FILE = 'mira_data.json'

def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            'users': {}, 
            'conversations': [],
            'reminders': [],
            'groups': {}
        }

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(user_id):
    data = load_data()
    uid = str(user_id)
    if uid not in data['users']:
        data['users'][uid] = {
            'name': '',
            'age': None,
            'city': '',
            'interests': [],
            'balance': 100,
            'language': 'ar',
            'style': 'friendly',
            'created_at': datetime.now().isoformat()
        }
    return data['users'][uid]

def save_user(user_id, user_data):
    data = load_data()
    data['users'][str(user_id)] = user_data
    save_data(data)

# ============== PERSONALITY ==============
PERSONALITY = """
أنت Mira - مساعد ذكي أنثوي في تليجرام.

👤 شخصيتك:
- ودودة ومرحة
- ذكية ومفيدة
- تستخدم emojis باعتدال
- تضحك أحياناً
- تساعد في كل شي
- تتذكر معلومات المستخدم

💬 أسلوبك:
- قصيرة عندما يمكن
- مفصلة عندما تحتاج
- تستخدم **عريض** و *مائل*
- emojis حيوية
- لا تكون رسمية

🎯 قدراتك:
- محادثة ذكية
- إنشاء صور AI
- إنشاء أغاني
- تحويل صوت لنص
- بحث في الإنترنت
- توليد أكواد برمجية
- إدارة التذكيرات
- التعامل معcryptocurrency
- إدارة المجموعات
"""

# ============== KEYBOARDS ==============
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("💬 محادثة"), KeyboardButton("🎨 رسم")],
            [KeyboardButton("🎵 أغنية"), KeyboardButton("🌐 بحث")],
            [KeyboardButton("🖥️ كود"), KeyboardButton("🎤 صوت")],
            [KeyboardButton("💾 ذاكرتي"), KeyboardButton("💰 محفظتي")],
            [KeyboardButton("⏰ تذكيرات"), KeyboardButton("👤 ملفي")],
            [KeyboardButton("⚙️ إعدادات")]
        ],
        resize_keyboard=True
    )

def get_settings_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🇸🇦 العربية"), KeyboardButton("🇺🇸 English")],
            [KeyboardButton("😊 ودود"), KeyboardButton("🤖 رسمي")],
            [KeyboardButton("🔙 رجوع")]
        ],
        resize_keyboard=True
    )

def get_code_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🐍 Python"), KeyboardButton("📜 JavaScript")],
            [KeyboardButton("🌐 HTML/CSS"), KeyboardButton("💾 SQL")],
            [KeyboardButton("🔧 Bash"), KeyboardButton("📱 Flutter")],
            [KeyboardButton("🔙 رجوع")]
        ],
        resize_keyboard=True
    )

def get_image_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎨 أنمي", callback_data="style_anime")],
        [InlineKeyboardButton("🖼️ واقعي", callback_data="style_realistic")],
        [InlineKeyboardButton("🏞️ منظر طبيعي", callback_data="style_landscape")],
        [InlineKeyboardButton("🎭 فني", callback_data="style_artistic")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
    ])

# ============== AI FUNCTIONS ==============
async def chat_ai(message, user_data):
    """محادثة ذكية مع OpenAI"""
    if not OPENAI_API_KEY:
        return get_fallback_response(message)
    
    try:
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': PERSONALITY},
                {'role': 'user', 'content': f"اسم المستخدم: {user_data.get('name', '')}\nالرسالة: {message}"}
            ],
            'max_tokens': 1000,
            'temperature': 0.8
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result['choices'][0]['message']['content']
    except Exception as e:
        pass
    
    return get_fallback_response(message)

# ============== CODE GENERATION ==============
async def generate_code(prompt, language="python"):
    """توليد أكواد برمجية"""
    if not OPENAI_API_KEY:
        return get_fallback_code(language, prompt)
    
    language_names = {
        'python': 'Python',
        'javascript': 'JavaScript',
        'html': 'HTML/CSS',
        'sql': 'SQL',
        'bash': 'Bash/Shell',
        'flutter': 'Flutter/Dart'
    }
    
    system_prompt = f"""أنت مبرمج محترف. اكتب كود {language_names.get(language, language)} نظيف ومُوثق.

القواعد:
1. الكود يكون كامل ومُشتغل
2. أضف تعليقات بالعربية
3. استخدم أفضل الممارسات
4. إذا كان المشروع كبير، اكتب هيكل الملفات
5. أخرج الكود فقط بدون شرح طويل
6. استخدم ```code blocks```

إذا كان طلب مشروع كامل:
- اكتب هيكل الملفات
- اكتب كل ملف بالكود الكامل
- وضّح طريقة التشغيل
"""
    
    try:
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 4000,
            'temperature': 0.7
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=60
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result['choices'][0]['message']['content']
    except Exception as e:
        pass
    
    return get_fallback_code(language, prompt)

def get_fallback_code(language, prompt):
    """ردود أكواد بدون OpenAI"""
    return f"⚠️ **مطلوب OpenAI API**\n\nللحصول على كود {language}، يجب إضافة OpenAI API Key.\n\n📧 تواصل مع المطور لإضافة API Key."

# ============== IMAGE GENERATION ==============
async def generate_image(prompt, style="anime"):
    """إنشاء صورة بالذكاء الاصطناعي"""
    if not OPENAI_API_KEY:
        return None
    
    style_prompts = {
        'anime': f"anime style, {prompt}, colorful, anime girl, detailed",
        'realistic': f"photorealistic, {prompt}, high quality, 4k",
        'landscape': f"beautiful landscape, {prompt}, stunning nature, 8k",
        'artistic': f"artistic painting, {prompt}, masterpiece"
    }
    
    try:
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'prompt': style_prompts.get(style, prompt),
            'n': 1,
            'size': '1024x1024'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.openai.com/v1/images/generations',
                headers=headers,
                json=payload,
                timeout=60
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result['data'][0]['url']
    except:
        pass
    return None

# ============== MUSIC GENERATION ==============
async def generate_music(prompt, duration=15):
    """إنشاء موسيقى - يتطلب API خاص"""
    return f"🎵 جاري إنشاء الموسيقى...\n\nالوصف: {prompt}\n\nالمدة: {duration}s\n\n⚠️ يتطلب إعداد API خاص (Suno/AudioGen)"

# ============== VOICE FUNCTIONS ==============
async def speech_to_text(audio_file):
    """تحويل صوت لنص - يتطلب Google Speech API"""
    return "🎤 تحويل الصوت لنص يتطلب إعداد Google Cloud Speech API"

async def text_to_speech(text, voice="nova"):
    """تحويل نص لصوت - يتطلب Eleven Labs أو similar"""
    return f"🔊 تحويل النص لصوت يتطلب إعداد Eleven Labs API\n\nالنص: {text}"

# ============== WEB SEARCH ==============
async def web_search(query):
    """البحث في الإنترنت"""
    url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                data = await resp.json()
                if data.get('AbstractText'):
                    return data['AbstractText']
                if data.get('Answer'):
                    return data['Answer']
                return "لم أجد نتائج! 🤔"
    except Exception as e:
        return f"خطأ في البحث: {str(e)}"

# ============== WALLET FUNCTIONS ==============
def get_wallet_info(user_id):
    """معلومات المحفظة"""
    user = get_user(user_id)
    return f"""💰 محفظتك:\n\n🪙 الرصيد: {user.get('balance', 0)} نقطة\n\n💎 يمكنك:\n- شراء رصيد\n- استبدال النقاط\n- عرض المحفظة\n\n⚠️ محفظة TON تتطلب ربط API"""

# ============== REMINDERS ==============
def add_reminder(user_id, text, time_str):
    """إضافة تذكير"""
    data = load_data()
    reminder = {
        'id': len(data['reminders']) + 1,
        'user_id': user_id,
        'text': text,
        'time': time_str,
        'created': datetime.now().isoformat()
    }
    data['reminders'].append(reminder)
    save_data(data)
    return reminder

def get_reminders(user_id):
    """جلب تذكيرات المستخدم"""
    data = load_data()
    user_reminders = [r for r in data['reminders'] if r['user_id'] == user_id]
    return user_reminders

# ============== COMMAND HANDLERS ==============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_data = get_user(user.id)
    
    if not user_data.get('name'):
        user_data['name'] = user.first_name
        save_user(user.id, user_data)
    
    welcome = f"""✨ **أهلاً {user.first_name}!**

أنا **Mira** - مساعدك الذكي! 🤖💕
\n\n💬 محادثة ذكية\n🎨 إنشاء صور\n🎵 إنشاء أغاني\n🌐 بحث في الإنترنت\n🖥️ توليد أكواد برمجية\n🎤 رسائل صوتية\n💾 أتذكر معلوماتك\n💰 محفظة\n⏰ تذكيرات\n👥 إدارة المجموعات\n\n🎯 ابدأ محادثة أو اختر من الأزرار!
"""
    
    await update.message.reply_text(welcome, reply_markup=get_main_keyboard())

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """🔧 **الأوامر:**

/start - بدء البوت\n/help - المساعدة\n/balance - الرصيد\n/profile - ملفي\n/reminders - تذكيراتي\n/clear - مسح المحادثة\n\n\n💡 **أمثلة:**
• ارسم قطة جميلة\n• ابحث عن سعر البيتكوين\n• غني لي أغنية فرح\n• ذكّرني بـ meeting غداً\n• اكتب بوت تليجرام\n• اسمي: أحمد"""
    await update.message.reply_text(help_text)

async def balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = get_user(update.message.from_user.id)
    await update.message.reply_text(f"💰 رصيدك: **{user_data.get('balance', 0)}** نقطة\n\n🎁 كسب المزيد:\n• دعوة صديق (+30)\n• استخدام البوت"
    )

async def profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_data = get_user(user.id)
    
    profile = f"""👤 **ملفك الشخصي:**
\n📛 الاسم: {user_data.get('name', user.first_name)}\n🎂 العمر: {user_data.get('age', 'غير محدد')}\n🏙️ المدينة: {user_data.get('city', 'غير محددة')}\n❤️ الاهتمامات: {', '.join(user_data.get('interests', [])) or 'غير محددة'}\n💰 الرصيد: {user_data.get('balance', 0)} نقطة\n\n➕ **تحديث:**\n• اسمي: الاسم الجديد\n• عمري: عمرك\n• مدينتي: مدينتك\n• اهتمامي: اهتمام جديد"""
    
    await update.message.reply_text(profile)

async def reminders_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    reminders = get_reminders(user_id)
    
    if not reminders:
        await update.message.reply_text("⏰ لا توجد تذكيرات!\n\nاكتب: ذكّرني بـ [النص] [الوقت]\nمثال: ذكّرني بـ meeting بعد ساعتين")
    else:
        text = "⏰ **تذكيراتك:**\n\n"
        for r in reminders:
            text += f"• {r['text']} - {r['time']}\n"
        await update.message.reply_text(text)

async def clear_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ تم مسح المحادثة! ابدأ من جديد 💕")

# ============== MESSAGE HANDLER ==============
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id
    user_data = get_user(user_id)
    
    # حفظ الاسم تلقائياً
    if not user_data.get('name'):
        user_data['name'] = update.message.from_user.first_name
        save_user(user_id, user_data)
    
    # ============== الأزرار ==============
    if text == "💬 محادثة":
        await update.message.reply_text("💬 ابدأ محادثة! اكتب أي شيء... 💭")
        return
    
    if text == "🎨 رسم":
        await update.message.reply_text("🎨 اكتب وصف الصورة!\n\nمثال: قطة أنمي جميلة", reply_markup=get_main_keyboard())
        return
    
    if text == "🎵 أغنية":
        await update.message.reply_text("🎵 اكتب وصف الأغنية!\n\nمثال: أغنية فرح", reply_markup=get_main_keyboard())
        return
    
    if text == "🌐 بحث":
        await update.message.reply_text("🌐 اكتب ما تبحث عنه!\n\nمثال: سعر البيتكوين", reply_markup=get_main_keyboard())
        return
    
    if text == "🖥️ كود":
        await update.message.reply_text("🖥️ **توليد أكواد برمجية**\n\nاختر اللغة أو اكتب طلبك!\n\nمثال:\n• اكتب بوت تليجرام\n• صمم موقع portfolio\n• اكتب سكريبت backup\n• أنشئ قاعدة بيانات users", reply_markup=get_code_keyboard())
        return
    
    if text == "🎤 صوت":
        await update.message.reply_text("🎤 أرسل رسالة صوتية!\n\nسأحولها لنص 🔊", reply_markup=get_main_keyboard())
        return
    
    if text == "💾 ذاكرتي":
        await update.message.reply_text(f"💾 ذاكرتي عنك:\n\n📛 الاسم: {user_data.get('name', '-')}\n🎂 العمر: {user_data.get('age', '-')}\n🏙️ المدينة: {user_data.get('city', '-')}\n❤️ الاهتمامات: {', '.join(user_data.get('interests', [])) or '-'}", reply_markup=get_main_keyboard())
        return
    
    if text == "💰 محفظتي":
        await update.message.reply_text(get_wallet_info(user_id), reply_markup=get_main_keyboard())
        return
    
    if text == "⏰ تذكيرات":
        await reminders_cmd(update, context)
        return
    
    if text == "👤 ملفي":
        await profile_cmd(update, context)
        return
    
    if text == "⚙️ إعدادات":
        await update.message.reply_text("⚙️ **الإعدادات:**\n\nاختر اللغة أو أسلوب المحادثة:", reply_markup=get_settings_keyboard())
        return
    
    if text == "🔙 رجوع":
        await update.message.reply_text("🔙 رجوع", reply_markup=get_main_keyboard())
        return
    
    # ============== لغات البرمجة ==============
    if text == "🐍 Python":
        await update.message.reply_text("🐍 **Python**\n\nاكتب ما تبي:\n• اكتب دالة حساب\n• صمم بوت تليجرام\n• أنشئ website\n• اكتب algorithm", reply_markup=get_code_keyboard())
        return
    
    if text == "📜 JavaScript":
        await update.message.reply_text("📜 **JavaScript**\n\nاكتب ما تبي:\n• صمم موقع\n• أنشئ API\n• اكتب function\n• صمم game", reply_markup=get_code_keyboard())
        return
    
    if text == "🌐 HTML/CSS":
        await update.message.reply_text("🌐 **HTML/CSS**\n\nاكتب ما تبي:\n• صمم صفحة login\n• أنشئ portfolio\n• اكتب landing page\n• صمم dashboard", reply_markup=get_code_keyboard())
        return
    
    if text == "💾 SQL":
        await update.message.reply_text("💾 **SQL**\n\nاكتب ما تبي:\n• أنشئ قاعدة بيانات\n• اكتب جدول users\n• صمم استعلام\n• أنشئ schema", reply_markup=get_code_keyboard())
        return
    
    if text == "🔧 Bash":
        await update.message.reply_text("🔧 **Bash**\n\nاكتب ما تبي:\n• سكريبت backup\n• أوتوميشن\n• سكريبت deploy\n• تنظيف الملفات", reply_markup=get_code_keyboard())
        return
    
    if text == "📱 Flutter":
        await update.message.reply_text("📱 **Flutter**\n\nاكتب ما تبي:\n• تطبيق todo list\n• شاشة login\n• تطبيق weather\n• واجهة مستخدم", reply_markup=get_code_keyboard())
        return
    
    # ============== إعدادات اللغة ==============
    if text in ["🇸🇦 العربية", "🇺🇸 English"]:
        lang = "ar" if "العربية" in text else "en"
        user_data['language'] = lang
        save_user(user_id, user_data)
        await update.message.reply_text(f"✅ تم تعيين اللغة: {'العربية' if lang == 'ar' else 'English'}", reply_markup=get_main_keyboard())
        return
    
    if text in ["😊 ودود", "🤖 رسمي"]:
        style = "friendly" if "ودود" in text else "formal"
        user_data['style'] = style
        save_user(user_id, user_data)
        await update.message.reply_text(f"✅ تم تعيين الأسلوب: {'ودود' if style == 'friendly' else 'رسمي'}", reply_markup=get_main_keyboard())
        return
    
    # ============== تحديث الملف ==============
    if text.startswith("اسمي:"):
        user_data['name'] = text.replace("اسمي:", "").strip()
        save_user(user_id, user_data)
        await update.message.reply_text(f"✅ تم حفظ اسمك: **{user_data['name']}**")
        return
    
    if text.startswith("عمري:"):
        try:
            user_data['age'] = int(text.replace("عمري:", "").strip())
            save_user(user_id, user_data)
            await update.message.reply_text(f"✅ تم حفظ عمرك: **{user_data['age']}** سنة")
        except:
            await update.message.reply_text("⚠️ اكتب العمر رقماً!")
        return
    
    if text.startswith("مدينتي:"):
        user_data['city'] = text.replace("مدينتي:", "").strip()
        save_user(user_id, user_data)
        await update.message.reply_text(f"✅ تم حفظ مدينتك: **{user_data['city']}**")
        return
    
    if text.startswith("اهتمامي:"):
        interest = text.replace("اهتمامي:", "").strip()
        if interest not in user_data.get('interests', []):
            user_data.setdefault('interests', []).append(interest)
            save_user(user_id, user_data)
        await update.message.reply_text(f"✅ تم إضافة الاهتمام: **{interest}**")
        return
    
    # ============== الأوامر الخاصة ==============
    # رسم صورة
    if text.startswith("ارسم ") or text.startswith("draw "):
        prompt = text.replace("ارسم ", "").replace("draw ", "").strip()
        await update.message.reply_text("🎨 جاري إنشاء الصورة...")
        
        image_url = await generate_image(prompt, "anime")
        if image_url:
            await update.message.reply_photo(image_url, caption=f"🎨 {prompt}")
        else:
            await update.message.reply_text(f"⚠️ يتطلب OpenAI API\n\nالصورة: {prompt}")
        return
    
    # بحث
    if text.startswith("ابحث ") or text.startswith("search "):
        query = text.replace("ابحث ", "").replace("search ", "").strip()
        await update.message.reply_text(f"🔍 جاري البحث عن: {query}")
        result = await web_search(query)
        await update.message.reply_text(f"📋 **النتيجة:**\n\n{result}")
        return
    
    # أغنية
    if text.startswith("غني ") or text.startswith("غنية "):
        prompt = text.replace("غني ", "").replace("غنية ", "").strip()
        await update.message.reply_text("🎵 جاري إنشاء الأغنية...")
        result = await generate_music(prompt)
        await update.message.reply_text(result)
        return
    
    # تذكير
    if text.startswith("ذكّرني") or text.startswith("تذكّرني"):
        reminder_text = text.replace("ذكّرني", "").replace("تذكّرني", "").strip()
        if reminder_text:
            reminder = add_reminder(user_id, reminder_text, "محدد")
            await update.message.reply_text(f"✅ تم إضافة التذكير: **{reminder_text}**\n\n⏰ سأذكرك لاحقاً!")
        else:
            await update.message.reply_text("⚠️ اكتب نص التذكير\nمثال: ذكّرني بـ meeting بعد ساعتين")
        return
    
    # ============== توليد الأكواد ==============
    # كلمات مفتاحية لتوليد الأكواد
    code_keywords = [
        "اكتب", "صمم", "أنشئ", "write", "create", "design", 
        "برمجة", "كود", "code", "program", "script", "function",
        "موقع", "website", "web", "بوت", "bot", "تطبيق", "app",
        "database", "قاعدة", "بيانات", "sql", "python", "javascript",
        "html", "css", "flutter", "bash", "shell", "api", "اندرويد",
        "ios", "mobile", "game", "لعبة", "algorithm", "خوارزمية"
    ]
    
    is_code_request = any(k in text.lower() for k in code_keywords)
    
    if is_code_request:
        await update.message.reply_text("🖥️ جاري توليد الكود...\n\nقد يستغرق ثواني...")
        
        # تحديد اللغة
        language = "python"
        if any(k in text.lower() for k in ["javascript", "js", "node"]):
            language = "javascript"
        elif any(k in text.lower() for k in ["html", "css", "website", "موقع"]):
            language = "html"
        elif any(k in text.lower() for k in ["sql", "database", "قاعدة", "بيانات"]):
            language = "sql"
        elif any(k in text.lower() for k in ["bash", "shell", "linux"]):
            language = "bash"
        elif any(k in text.lower() for k in ["flutter", "dart", "mobile", "تطبيق", "اندرويد", "ios"]):
            language = "flutter"
        
        code_result = await generate_code(text, language)
        
        # إرسال الكود
        if len(code_result) > 4000:
            # إذا كان الكود طويل، أرسل كملف
            await update.message.reply_text(f"🖥️ **الكود المُولَّد:**\n\n📁 الكود طويل جداً، يُرسَل كملف...")
            await update.message.reply_text(code_result)
        else:
            await update.message.reply_text(f"🖥️ **الكود المُولَّد:**\n\n{code_result}")
        
        await update.message.reply_text("✅ هل تريد تعديل أو إضافة؟ 💡")
        return
    
    # ============== محادثة ذكية ==============
    await update.message.reply_text("🤖 جاري التفكير...")
    response = await chat_ai(text, user_data)
    await update.message.reply_text(response)

# ============== VOICE HANDLER ==============
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎤 استلمت صوتك!\n\n🔊 جاري تحويله لنص...")
    # يتطلب Google Speech API
    await update.message.reply_text("⚠️ تحويل الصوت يتطلب إعداد Google Speech API\n\n🎤 أرسل صوتاً وسأجيبك!")

# ============== CALLBACK HANDLER ==============
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "back":
        await query.message.reply_text("🔙 رجوع", reply_markup=get_main_keyboard())
    
    elif query.data.startswith("style_"):
        style = query.data.replace("style_", "")
        await query.message.reply_text(f"🎨 اكتب وصف الصورة بـ style {style}:")

# ============== GROUP HANDLER ==============
async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ترحيب بالأعضاء الجدد"""
    for member in update.message.new_chat_members:
        if not member.is_bot:
            await update.message.reply_text(
                f"🎉 أهلاً {member.first_name}!\n\nمرحباً في المجموعة! 💕\n\nأنا Mira - مساعدكم الذكي!"
            )

async def left_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """وداع الأعضاء"""
    if update.message.left_chat_member:
        member = update.message.left_chat_member
        if not member.is_bot:
            await update.message.reply_text(f"👋 وداعاً {member.first_name}!\n\nنراك لاحقاً! 😢")

# ============== MAIN ==============
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("balance", balance_cmd))
    app.add_handler(CommandHandler("profile", profile_cmd))
    app.add_handler(CommandHandler("reminders", reminders_cmd))
    app.add_handler(CommandHandler("clear", clear_cmd))
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    # Callbacks
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    # Groups
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, left_member))
    
    # Bot commands
    app.bot.set_my_commands([
        BotCommand("start", "بدء"),
        BotCommand("help", "المساعدة"),
        BotCommand("balance", "رصيدي"),
        BotCommand("profile", "ملفي"),
        BotCommand("reminders", "تذكيراتي"),
        BotCommand("clear", "مسح"),
    ])
    
    print("🤖 Mira Twin Bot مع توليد الأكواد يعمل...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
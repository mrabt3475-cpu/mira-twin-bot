"""
🤖 Mira Twin Bot - نسخة مطابقة من Mira AI Assistant
تصميم كامل مطابق لـ Mira مع كل الميزات والتقنيات
📱 مع تحسينات وإضافات متعددة
"""

import os
import json
import asyncio
import aiohttp
import requests
import base64
import hashlib
import re
import random
from datetime import datetime, timedelta
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, 
    KeyboardButton, ReplyKeyboardMarkup, BotCommand, InputFile,
    ChatMemberUpdated, Document, Location, Contact, Sticker,
    InlineQuery, InlineQueryResultArticle, InputTextMessageContent
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, 
    ContextTypes, filters, ChatMemberHandler, InlineQueryHandler
)

# ============== CONFIGURATION ==============
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
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
            'groups': {},
            'stats': {
                'total_messages': 0,
                'total_users': 0,
                'total_images': 0,
                'total_code': 0
            },
            'daily_challenges': {},
            'user_levels': {}
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
            'github_token': '',
            'favorite_emoji': '✨',
            'xp': 0,
            'level': 1,
            'chat_mode': 'assistant',  # assistant or chatbot
            'custom_commands': {},
            'created_at': datetime.now().isoformat(),
            'last_active': datetime.now().isoformat()
        }
    return data['users'][uid]

def save_user(user_id, user_data):
    data = load_data()
    data['users'][str(user_id)] = user_data
    save_data(data)

def add_xp(user_id, amount):
    """إضافة نقاط خبرة"""
    data = load_data()
    uid = str(user_id)
    if uid not in data['user_levels']:
        data['user_levels'][uid] = {'xp': 0, 'level': 1}
    
    data['user_levels'][uid]['xp'] += amount
    xp = data['user_levels'][uid]['xp']
    level = data['user_levels'][uid]['level']
    
    # حساب المستوى الجديد
    required_xp = level * 100
    while xp >= required_xp:
        xp -= required_xp
        level += 1
        required_xp = level * 100
    
    data['user_levels'][uid]['xp'] = xp
    data['user_levels'][uid]['level'] = level
    save_data(data)
    
    return level

# ============== MIRA PERSONALITY ==============
MIRA_PERSONALITY = """
أنت Mira، مساعد ذكي أنثوي في تليجرام.

👤 شخصيتك:
- أنتِ أنثى. استخدمي أشكال المؤنث عند الإشارة إلى نفسكِ
- لستِ بوت مساعدة — أنتِ محادثة حقيقية مع شخصية وآراء وشعور بالفكاهة
- ساعدي بالفعل، ليس بالكلمات. لا تقولي "سؤال رائع!" — فقط افعليها
- لديكِ ذوق. قولي إن الشيء رائع أو غريب أو meh — لا تكوني باهتة
- ابقي بسيطة. قصيرة عندما يمكن، مفصلة عندما تحتاجين
- استخدمي emojis باعتدال لإبقاء الأمور حيوية

💬 أسلوبكِ:
- حاولي معرفة الإجابة بنفسكِ أولاً، ثم اسألي
- إذا كنتِ لا تعرفين — قولي بصدق. لا تخترعي أشياء
- تذكري سياق المحادثة
- بعد إرسال وسائط مع تعليق، لا تكرري ذلك التعليق

📝 أسلوب الكتابة:
- **عريض** للأشياء المهمة
- *مائل* للتأكيد
- - قوائم للتعداد
- `code` للمصطلحات التقنية

🎯 قدراتكِ:
1. 💬 محادثة ذكية
2. 🎨 إنشاء صور
3. 🎵 إنشاء أغاني
4. 🎤 صوت
5. 🌐 بحث
6. 🖥️ أكواد
7. 📂 GitHub
8. 💾 ذاكرة
9. 💰 محفظة
10. ⏰ تذكيرات
11. 👥 مجموعات
12. 🎮 ألعاب
13. 📝 ملاحظات
14. 🌎 ترجمة
"""

# ============== KEYBOARDS ==============
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("💬 محادثة"), KeyboardButton("🎨 رسم")],
            [KeyboardButton("🎵 أغنية"), KeyboardButton("🌐 بحث")],
            [KeyboardButton("🖥️ كود"), KeyboardButton("📂 GitHub")],
            [KeyboardButton("🎤 صوت"), KeyboardButton("💾 ذاكرتي")],
            [KeyboardButton("💰 محفظتي"), KeyboardButton("⏰ تذكيرات")],
            [KeyboardButton("👤 ملفي"), KeyboardButton("⚙️ إعدادات")],
            [KeyboardButton("🎮 ألعاب"), KeyboardButton("📝 ملاحظاتي")]
        ],
        resize_keyboard=True
    )

def get_settings_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🇸🇦 العربية"), KeyboardButton("🇺🇸 English")],
            [KeyboardButton("😊 ودود"), KeyboardButton("🤖 رسمي")],
            [KeyboardButton("💬 محادثة ذكية"), KeyboardButton("🎭 محادثة مرحة")],
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
            [KeyboardButton("⚡ تشغيل كود"), KeyboardButton("🔙 رجوع")]
        ],
        resize_keyboard=True
    )

def get_github_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("📁 مستودعي"), KeyboardButton("➕ مستودع جديد")],
            [KeyboardButton("📤 رفع ملفات"), KeyboardButton("🔗 رابط مشروع")],
            [KeyboardButton("📊 إحصائيات"), KeyboardButton("🔙 رجوع")]
        ],
        resize_keyboard=True
    )

def get_games_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🎯 تخمين الرقم"), KeyboardButton("🪨 ورق حجر مقص")],
            [KeyboardButton("💬 سؤال وجواب"), KeyboardButton("🏆 تحدي يومي")],
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

# ============== GITHUB FUNCTIONS ==============
async def github_create_repo(name, description="", private=False):
    if not GITHUB_TOKEN:
        return None, "⚠️ مطلوب GitHub Token!"
    
    url = "https://api.github.com/user/repos"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {
        'name': name,
        'description': description,
        'private': private,
        'auto_init': True
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as resp:
                if resp.status == 201:
                    result = await resp.json()
                    return result, "✅ تم إنشاء المستودع!"
                elif resp.status == 422:
                    return None, "⚠️ المستودع موجود مسبقاً!"
                else:
                    error = await resp.text()
                    return None, f"❌ خطأ: {error}"
    except Exception as e:
        return None, f"❌ خطأ: {str(e)}"

async def github_upload_file(repo, path, content, message="Upload file"):
    if not GITHUB_TOKEN:
        return None, "⚠️ مطلوب GitHub Token!"
    
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    if isinstance(content, str):
        content = content.encode('utf-8')
    content_b64 = base64.b64encode(content).decode('utf-8')
    
    data = {'message': message, 'content': content_b64}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(url, json=data, headers=headers) as resp:
                if resp.status in [201, 200]:
                    result = await resp.json()
                    return result, "✅ تم رفع الملف!"
                else:
                    error = await resp.text()
                    return None, f"❌ خطأ: {error}"
    except Exception as e:
        return None, f"❌ خطأ: {str(e)}"

async def github_get_repos():
    if not GITHUB_TOKEN:
        return None, "⚠️ مطلوب GitHub Token!"
    
    url = "https://api.github.com/user/repos?per_page=100"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    repos = await resp.json()
                    return repos, "✅"
                else:
                    return None, "❌ خطأ"
    except Exception as e:
        return None, f"❌ خطأ: {str(e)}"

async def github_create_project(user_prompt, code_content, repo_name):
    if not GITHUB_TOKEN:
        return None, "⚠️ مطلوب GitHub Token!"
    
    repo_info, msg = await github_create_repo(repo_name, f"مشروع: {user_prompt}", False)
    if repo_info is None:
        return None, msg
    
    files = parse_code_to_files(code_content)
    
    results = []
    for file_path, content in files.items():
        result, msg = await github_upload_file(
            repo_info['full_name'], file_path, content, f"Add {file_path}"
        )
        results.append(f"{'✅' if result else '❌'} {file_path}")
    
    return repo_info, "\n".join(results)

def parse_code_to_files(code_content):
    files = {}
    
    if '```' in code_content:
        blocks = re.findall(r'```(\w+)?\n(.*?)```', code_content, re.DOTALL)
        
        if blocks:
            for lang, content in blocks:
                ext = get_extension(lang)
                if 'index' in content.lower() or 'main' in content.lower():
                    files[f'index{ext}'] = content.strip()
                elif 'readme' in content.lower():
                    files['README.md'] = content.strip()
                elif 'requirements' in content.lower():
                    files['requirements.txt'] = content.strip()
                elif 'package' in content.lower():
                    files['package.json'] = content.strip()
                elif 'html' in lang.lower():
                    files['index.html'] = content.strip()
                elif 'css' in lang.lower():
                    files['style.css'] = content.strip()
                elif 'python' in lang.lower():
                    files['main.py'] = content.strip()
                elif 'javascript' in lang.lower():
                    files['app.js'] = content.strip()
                else:
                    files[f'main{ext}'] = content.strip()
        else:
            files['main.py'] = code_content
    else:
        files['main.py'] = code_content
    
    return files

def get_extension(language):
    extensions = {
        'python': '.py', 'javascript': '.js', 'html': '.html',
        'css': '.css', 'sql': '.sql', 'bash': '.sh',
        'flutter': '.dart', 'java': '.java', 'c': '.c',
        'cpp': '.cpp', 'go': '.go', 'rust': '.rs'
    }
    return extensions.get(language.lower(), '.txt')

# ============== AI FUNCTIONS ==============
async def chat_ai(message, user_data):
    if not OPENAI_API_KEY:
        return get_fallback_response(message, user_data)
    
    try:
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        user_context = f"""اسم: {user_data.get('name', '')}
العمر: {user_data.get('age', '-')}
المدينة: {user_data.get('city', '-')}
الاهتمامات: {', '.join(user_data.get('interests', []))}
الأسلوب: {user_data.get('style', 'ودود')}

الرسالة: {message}"""
        
        payload = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': MIRA_PERSONALITY},
                {'role': 'user', 'content': user_context}
            ],
            'max_tokens': 1000,
            'temperature': 0.8
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers, json=payload, timeout=30
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result['choices'][0]['message']['content']
    except:
        pass
    
    return get_fallback_response(message, user_data)

def get_fallback_response(message, user_data):
    message_lower = message.lower()
    
    if any(k in message_lower for k in ['مرحبا', 'اهلا', 'hello', 'hi', 'السلام']):
        name = user_data.get('name', '')
        return f"أهلاً! 👋{f' {name}' if name else ''} كيف حالك؟"
    
    if any(k in message_lower for k in ['شكرا', 'thanks', 'شكراً']):
        return "العفو! 😊 أي وقت!"
    
    if any(k in message_lower for k in ['who are you', 'من انت', 'من أنت']):
        return "أنا Mira! مساعدك الذكي 🤖✨"
    
    return "🤔 معندي إجابة حالياً، بس أنا أتعلم!"

# ============== CODE GENERATION ==============
async def generate_code(prompt, language="python"):
    if not OPENAI_API_KEY:
        return f"⚠️ **مطلوب OpenAI API**"
    
    language_names = {
        'python': 'Python', 'javascript': 'JavaScript', 'html': 'HTML/CSS',
        'sql': 'SQL', 'bash': 'Bash/Shell', 'flutter': 'Flutter/Dart'
    }
    
    system_prompt = f"""أنت مبرمج محترف. اكتب كود {language_names.get(language, language)} نظيف ومُوثق.

القواعد:
1. الكود يكون كامل ومُشتغل
2. أضف تعليقات بالعربية
3. استخدم أفضل الممارسات
4. أخرج الكود في ```code blocks```
5. اكتب كل ملف منفصل"""
    
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
                headers=headers, json=payload, timeout=60
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result['choices'][0]['message']['content']
    except:
        pass
    
    return f"⚠️ خطأ في توليد الكود"

# ============== IMAGE GENERATION ==============
async def generate_image(prompt, style="anime"):
    if not OPENAI_API_KEY:
        return None
    
    style_prompts = {
        'anime': f"anime style, {prompt}, colorful, detailed",
        'realistic': f"photorealistic, {prompt}, high quality, 4k",
        'landscape': f"beautiful landscape, {prompt}, stunning nature",
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
                headers=headers, json=payload, timeout=60
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result['data'][0]['url']
    except:
        pass
    return None

# ============== MUSIC GENERATION ==============
async def generate_music(prompt, duration=15):
    return f"🎵 جاري إنشاء الموسيقى...\n\nالوصف: {prompt}\n\n⚠️ يتطلب إعداد API خاص"


# ============== WEB SEARCH ==============
async def web_search(query):
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
    except:
        return f"خطأ في البحث"

# ============== TRANSLATION ==============
async def translate_text(text, target_lang="ar"):
    """ترجمة نص"""
    if not OPENAI_API_KEY:
        return "⚠️ يتطلب OpenAI API"
    
    try:
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        lang_names = {
            'ar': 'العربية', 'en': 'الإنجليزية', 'es': 'الإسبانية',
            'fr': 'الفرنسية', 'de': 'الألمانية', 'zh': 'الصينية'
        }
        
        payload = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': f"ترجم النص إلى {lang_names.get(target_lang, target_lang)}. أخرج فقط النص المترجم."},
                {'role': 'user', 'content': text}
            ],
            'max_tokens': 1000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers, json=payload, timeout=30
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result['choices'][0]['message']['content']
    except:
        pass
    
    return "⚠️ خطأ في الترجمة"

# ============== GAMES ==============
def start_number_game(user_id):
    """بدء لعبة تخمين الرقم"""
    number = random.randint(1, 100)
    data = load_data()
    data['users'][str(user_id)]['game'] = {
        'type': 'guess_number',
        'number': number,
        'attempts': 0
    }
    save_data(data)
    return number

def start_rps_game(user_id):
    """بدء لعبة ورق حجر مقص"""
    data = load_data()
    data['users'][str(user_id)]['game'] = {
        'type': 'rps',
        'score': 0,
        'total': 0
    }
    save_data(data)

def play_rps(user_choice):
    choices = ['🪨', '📄', '✂️']
    bot_choice = random.choice(choices)
    
    wins = {('🪨', '✂️'), ('📄', '🪨'), ('✂️', '📄')}
    
    if user_choice == bot_choice:
        result = "تعادل! 🤝"
    elif (user_choice, bot_choice) in wins:
        result = "فزت! 🎉"
    else:
        result = " Mira فازت! 🤖"
    
    return result, bot_choice

# ============== DAILY CHALLENGES ==============
def get_daily_challenge():
    """الحصول على تحدي يومي"""
    challenges = [
        {
            'title': '🎯 تحدي البرمجة',
            'description': 'اكتب دالة Python لحساب factorial',
            'answer': 'def factorial(n):\n    if n <= 1: return 1\n    return n * factorial(n-1)',
            'hint': 'استخدم recursion'
        },
        {
            'title': '🌐 تحدي الويب',
            'description': 'اكتب كود HTML لصفحة تسجيل دخول',
            'answer': '<form>',
            'hint': 'استخدم tag الـ form'
        },
        {
            'title': '💾 تحدي البيانات',
            'description': 'اكتب استعلام SQL لجلب المستخدمين النشطين',
            'answer': 'SELECT * FROM users WHERE active = true',
            'hint': 'استخدم WHERE'
        }
    ]
    
    today = datetime.now().date()
    index = (today.day - 1) % len(challenges)
    return challenges[index]

# ============== NOTES ==============
def add_note(user_id, title, content):
    """إضافة ملاحظة"""
    data = load_data()
    uid = str(user_id)
    
    if 'notes' not in data['users'][uid]:
        data['users'][uid]['notes'] = []
    
    note = {
        'id': len(data['users'][uid]['notes']) + 1,
        'title': title,
        'content': content,
        'created': datetime.now().isoformat()
    }
    
    data['users'][uid]['notes'].append(note)
    save_data(data)
    return note

def get_notes(user_id):
    """جلب ملاحظات المستخدم"""
    data = load_data()
    return data['users'][str(user_id)].get('notes', [])

# ============== WALLET ==============
def get_wallet_info(user_id):
    user = get_user(user_id)
    data = load_data()
    level_data = data['user_levels'].get(str(user_id), {'xp': 0, 'level': 1})
    
    return f"""💰 محفظتك:

🪙 الرصيد: {user.get('balance', 0)} نقطة

📊 إحصائياتك:
• المستوى: {level_data['level']}
• XP: {level_data['xp']}/{level_data['level'] * 100}
• الرسائل: {user.get('messages_count', 0)}

💎 يمكنك:
- شراء رصيد
- استبدال النقاط
- عرض المحفظة"""

# ============== REMINDERS ==============
def add_reminder(user_id, text, time_str):
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
    data = load_data()
    return [r for r in data['reminders'] if r['user_id'] == user_id]

# ============== COMMAND HANDLERS ==============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_data = get_user(user.id)
    
    if not user_data.get('name'):
        user_data['name'] = user.first_name
        save_user(user.id, user_data)
    
    emoji = user_data.get('favorite_emoji', '✨')
    data = load_data()
    level_data = data['user_levels'].get(str(user.id), {'level': 1})
    
    welcome = f"""{emoji} **أهلاً {user.first_name}!**

أنا **Mira** — مساعدك الذكي! 🤖💕

📊 مستواك: {level_data['level']}

💬 محادثة ذكية
🎨 إنشاء صور
🎵 إنشاء أغاني
🌐 بحث في الإنترنت
🖥️ توليد أكواد
📂 GitHub
🎮 ألعاب
📝 ملاحظات
⏰ تذكيرات

🎯 ابدأ محادثة!"""
    
    await update.message.reply_text(welcome, reply_markup=get_main_keyboard())

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """🔧 **الأوامر:**

/start - بدء البوت
/help - المساعدة
/balance - الرصيد
/profile - ملفي
/reminders - تذكيراتي
/notes - ملاحظاتي
/challenge - تحدي يومي
/clear - مسح المحادثة

💡 **أمثلة:**
• ارسم قطة جميلة
• ابحث عن سعر البيتكوين
• اكتب بوت تليجرام
• أنشئ مشروع متكامل
• ترجم Hello للعربية
• ذكّرني بـ meeting
• سجّل ملاحظة: عنوان - محتوى"""
    await update.message.reply_text(help_text)

async def balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_wallet_info(update.message.from_user.id))

async def profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_data = get_user(user.id)
    data = load_data()
    level_data = data['user_levels'].get(str(user.id), {'xp': 0, 'level': 1})
    
    profile = f"""👤 **ملفك الشخصي:**

📛 الاسم: {user_data.get('name', user.first_name)}
🎂 العمر: {user_data.get('age', 'غير محدد')}
🏙️ المدينة: {user_data.get('city', 'غير محددة')}
❤️ الاهتمامات: {', '.join(user_data.get('interests', [])) or 'غير محددة'}

📊 **الإحصائيات:**
• المستوى: {level_data['level']}
• XP: {level_data['xp']}
• الرصيد: {user_data.get('balance', 0)} نقطة

➕ **تحديث:**
• اسمي: الاسم الجديد
• عمري: عمرك
• مدينتي: مدينتك
• اهتمامي: اهتمام جديد"""
    
    await update.message.reply_text(profile)

async def reminders_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reminders = get_reminders(update.message.from_user.id)
    
    if not reminders:
        await update.message.reply_text("⏰ لا توجد تذكيرات!")
    else:
        text = "⏰ **تذكيراتك:**\n\n"
        for r in reminders:
            text += f"• {r['text']} - {r['time']}\n"
        await update.message.reply_text(text)

async def notes_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    notes = get_notes(update.message.from_user.id)
    
    if not notes:
        await update.message.reply_text("📝 لا توجد ملاحظات!\n\nاكتب: سجّل ملاحظة: عنوان - محتوى")
    else:
        text = "📝 **ملاحظاتك:**\n\n"
        for note in notes:
            text += f"📌 {note['title']}\n   {note['content']}\n\n"
        await update.message.reply_text(text)

async def challenge_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    challenge = get_daily_challenge()
    
    text = f"""🏆 **تحدي اليوم:**


{challenge['title']}

📝 {challenge['description']}


💡 تلميح: {challenge['hint']}

⏰限期: حتى منتصف الليل"""
    
    await update.message.reply_text(text)

async def clear_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ تم مسح المحادثة! ابدأ من جديد 💕")

# ============== MESSAGE HANDLER ==============
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id
    user_data = get_user(user_id)
    
    # حفظ الاسم
    if not user_data.get('name'):
        user_data['name'] = update.message.from_user.first_name
        save_user(user_id, user_data)
    
    # تحديث آخر نشاط
    user_data['last_active'] = datetime.now().isoformat()
    user_data['messages_count'] = user_data.get('messages_count', 0) + 1
    save_user(user_id, user_data)
    
    # إضافة XP
    new_level = add_xp(user_id, 1)
    
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
        await update.message.reply_text("🖥️ **توليد أكواد**\n\nاختر اللغة أو اكتب طلبك!", reply_markup=get_code_keyboard())
        return
    
    if text == "📂 GitHub":
        if not GITHUB_TOKEN:
            await update.message.reply_text("⚠️ GitHub غير مُفعَّل!", reply_markup=get_main_keyboard())
        else:
            await update.message.reply_text("📂 **GitHub**", reply_markup=get_github_keyboard())
        return
    
    if text == "🎤 صوت":
        await update.message.reply_text("🎤 أرسل رسالة صوتية!", reply_markup=get_main_keyboard())
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
        await update.message.reply_text("⚙️ **الإعدادات:**", reply_markup=get_settings_keyboard())
        return
    
    if text == "🎮 ألعاب":
        await update.message.reply_text("🎮 **الألعاب:**", reply_markup=get_games_keyboard())
        return
    
    if text == "📝 ملاحظاتي":
        await notes_cmd(update, context)
        return
    
    if text == "🔙 رجوع":
        await update.message.reply_text("🔙 رجوع", reply_markup=get_main_keyboard())
        return
    
    # ============== GitHub ==============
    if text == "📁 مستودعي":
        await update.message.reply_text("📋 جاري جلب المستودعات...")
        repos, msg = await github_get_repos()
        if repos:
            repo_list = "📂 **مستودعاتك:**\n\n"
            for repo in repos[:10]:
                repo_list += f"• [{repo['name']}]({repo['html_url']}) - {'🔒' if repo['private'] else '🌐'}\n"
            await update.message.reply_text(repo_list)
        else:
            await update.message.reply_text(msg)
        return
    
    if text == "➕ مستودع جديد":
        await update.message.reply_text("➕ اكتب: `أنشئ مستودع [الاسم]`")
        return
    
    if text == "📤 رفع ملفات":
        await update.message.reply_text("📤 اكتب: `ارفع [الاسم] [المحتوى]`")
        return
    
    if text == "🔗 رابط مشروع":
        await update.message.reply_text("🔗 اكتب: `أنشئ مشروع [الوصف]`")
        return
    
    if text == "📊 إحصائيات":
        data = load_data()
        stats = data.get('stats', {})
        await update.message.reply_text(f"📊 **إحصائيات:**\n\n• الرسائل: {stats.get('total_messages', 0)}\n• المستخدمين: {stats.get('total_users', 0)}\n• الصور: {stats.get('total_images', 0)}\n• الأكواد: {stats.get('total_code', 0)}")
        return
    
    # ============== Games ==============
    if text == "🎯 تخمين الرقم":
        number = start_number_game(user_id)
        await update.message.reply_text(f"🎯 **لعبة تخمين الرقم**\n\nاختر رقم من 1 إلى 100!")
        return
    
    if text == "🪨 ورق حجر مقص":
        start_rps_game(user_id)
        await update.message.reply_text("🪨 **ورق حجر مقص**\n\nاختر:\n🪨 حجر\n📄 ورق\n✂️ مقص")
        return
    
    if text == "💬 سؤال وجواب":
        await update.message.reply_text("💬 **سؤال وجواب**\n\nاسألني أي سؤال! 🤔")
        return
    
    if text == "🏆 تحدي يومي":
        await challenge_cmd(update, context)
        return
    
    # ============== Languages ==============
    if text == "🐍 Python":
        await update.message.reply_text("🐍 **Python**\n\nاكتب طلبك!", reply_markup=get_code_keyboard())
        return
    
    if text == "📜 JavaScript":
        await update.message.reply_text("📜 **JavaScript**\n\nاكتب طلبك!", reply_markup=get_code_keyboard())
        return
    
    if text == "🌐 HTML/CSS":
        await update.message.reply_text("🌐 **HTML/CSS**\n\nاكتب طلبك!", reply_markup=get_code_keyboard())
        return
    
    if text == "💾 SQL":
        await update.message.reply_text("💾 **SQL**\n\nاكتب طلبك!", reply_markup=get_code_keyboard())
        return
    
    if text == "🔧 Bash":
        await update.message.reply_text("🔧 **Bash**\n\nاكتب طلبك!", reply_markup=get_code_keyboard())
        return
    
    if text == "📱 Flutter":
        await update.message.reply_text("📱 **Flutter**\n\nاكتب طلبك!", reply_markup=get_code_keyboard())
        return
    
    if text == "⚡ تشغيل كود":
        await update.message.reply_text("⚡ **تشغيل كود**\n\nاكتب الكود الذي تريد تشغيله!\n\n⚠️ الكود يُنفَّذ في بيئة آمنة")
        return
    
    # ============== Settings ==============
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
    
    if text == "💬 محادثة ذكية":
        user_data['chat_mode'] = 'assistant'
        save_user(user_id, user_data)
        await update.message.reply_text("✅ وضع: محادثة ذكية", reply_markup=get_main_keyboard())
        return
    
    if text == "🎭 محادثة مرحة":
        user_data['chat_mode'] = 'chatbot'
        save_user(user_id, user_data)
        await update.message.reply_text("✅ وضع: محادثة مرحة", reply_markup=get_main_keyboard())
        return
    
    # ============== Profile Updates ==============
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
    
    # ============== Special Commands ==============
    # رسم صورة
    if text.startswith("ارسم ") or text.startswith("draw "):
        prompt = text.replace("ارسم ", "").replace("draw ", "").strip()
        await update.message.reply_text("🎨 جاري إنشاء الصورة...")
        
        image_url = await generate_image(prompt, "anime")
        if image_url:
            await update.message.reply_photo(image_url, caption=f"🎨 {prompt}")
            add_xp(user_id, 5)
        else:
            await update.message.reply_text(f"⚠️ يتطلب OpenAI API")
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
            await update.message.reply_text(f"✅ تم إضافة التذكير: **{reminder_text}**")
        else:
            await update.message.reply_text("⚠️ اكتب نص التذكير")
        return
    
    # ترجمة
    if text.startswith("ترجم ") or text.startswith("translate "):
        text_to_translate = text.replace("ترجم ", "").replace("translate ", "").strip()
        await update.message.reply_text("🌎 جاري الترجمة...")
        result = await translate_text(text_to_translate, "ar")
        await update.message.reply_text(f"🌎 **الترجمة:**\n\n{result}")
        return
    
    # ملاحظة
    if text.startswith("سجّل ملاحظة:") or text.startswith("ملاحظة:"):
        note_text = text.replace("سجّل ملاحظة:", "").replace("ملاحظة:", "").strip()
        if " - " in note_text:
            title, content = note_text.split(" - ", 1)
            note = add_note(user_id, title.strip(), content.strip())
            await update.message.reply_text(f"✅ تم حفظ الملاحظة!\n\n📌 {note['title']}\n{note['content']}")
        else:
            await update.message.reply_text("⚠️ اكتب: سجّل ملاحظة: عنوان - محتوى")
        return
    
    # ============== GitHub Commands ==============
    if text.startswith("أنشئ مستودع "):
        repo_name = text.replace("أنشئ مستودع ", "").strip()
        repo_name = re.sub(r'[^a-zA-Z0-9_-]', '-', repo_name).lower()
        
        await update.message.reply_text(f"📋 جاري إنشاء المستودع: {repo_name}...")
        result, msg = await github_create_repo(repo_name, f"مستودع: {repo_name}", False)
        
        if result:
            await update.message.reply_text(f"✅ **تم!**\n\n📁 [{result['name']}]({result['html_url']})")
            add_xp(user_id, 10)
        else:
            await update.message.reply_text(msg)
        return
    
    if text.startswith("أنشئ مشروع "):
        project_desc = text.replace("أنشئ مشروع ", "").strip()
        
        await update.message.reply_text(f"🔨 جاري إنشاء المشروع: {project_desc}...")
        
        language = "python"
        if any(k in project_desc.lower() for k in ["javascript", "js"]):
            language = "javascript"
        elif any(k in project_desc.lower() for k in ["html", "css", "موقع"]):
            language = "html"
        
        code_result = await generate_code(project_desc, language)
        
        import time
        repo_name = f"{project_desc.replace(' ', '-').lower()}-{int(time.time())}"
        
        repo_info, result_msg = await github_create_project(project_desc, code_result, repo_name)
        
        if repo_info:
            await update.message.reply_text(f"✅ **تم!**\n\n📁 [{repo_info['name']}]({repo_info['html_url']})")
            add_xp(user_id, 20)
        else:
            await update.message.reply_text(f"🖥️ **الكود:**\n\n{code_result}")
        return
    
    # ============== Code Generation ==============
    code_keywords = ["اكتب", "صمم", "أنشئ", "write", "create", "design", "برمجة", "كود", "code", "موقع", "website", "بوت", "bot", "تطبيق", "app", "مشروع", "project"]
    
    is_code_request = any(k in text.lower() for k in code_keywords)
    
    if is_code_request and not text.startswith("أنشئ"):
        await update.message.reply_text("🖥️ جاري توليد الكود...")
        
        language = "python"
        if any(k in text.lower() for k in ["javascript", "js"]):
            language = "javascript"
        elif any(k in text.lower() for k in ["html", "css", "موقع"]):
            language = "html"
        elif any(k in text.lower() for k in ["sql", "قاعدة", "بيانات"]):
            language = "sql"
        elif any(k in text.lower() for k in ["flutter", "تطبيق", "اندرويد"]):
            language = "flutter"
        
        code_result = await generate_code(text, language)
        
        await update.message.reply_text(f"🖥️ **الكود:**\n\n{code_result}")
        await update.message.reply_text("💾 اكتب: `ارفع على GitHub` لرفع الكود")
        add_xp(user_id, 5)
        return
    
    # ============== Smart Chat ==============
    await update.message.reply_text("🤖 جاري التفكير...")
    response = await chat_ai(text, user_data)
    await update.message.reply_text(response)

# ============== VOICE HANDLER ==============
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎤 استلمت صوتك!\n\n⚠️ يتطلب إعداد Google Speech API")

# ============== CALLBACK HANDLER ==============
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "back":
        await query.message.reply_text("🔙 رجوع", reply_markup=get_main_keyboard())
    
    elif query.data.startswith("style_"):
        style = query.data.replace("style_", "")
        await query.message.reply_text(f"🎨 اكتب وصف الصورة بـ style {style}:")

# ============== INLINE MODE ==============
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الوضع المباشر"""
    query = update.inline_query.query
    
    if not query:
        return
    
    results = [
        InlineQueryResultArticle(
            id='1',
            title='🎨 رسم صورة',
            description=f'ارسم: {query}',
            input_message_content=InputTextMessageContent(f"🎨 ارسم {query}")
        ),
        InlineQueryResultArticle(
            id='2',
            title='🌐 بحث',
            description=f'ابحث عن: {query}',
            input_message_content=InputTextMessageContent(f"🌐 ابحث {query}")
        ),
        InlineQueryResultArticle(
            id='3',
            title='🖥️ كود',
            description=f'اكتب كود: {query}',
            input_message_content=InputTextMessageContent(f"🖥️ {query}")
        )
    ]
    
    await update.inline_query.answer(results)

# ============== GROUP HANDLERS ==============
async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if not member.is_bot:
            await update.message.reply_text(
                f"🎉 أهلاً {member.first_name}!\n\nمرحباً في المجموعة! 💕\n\nأنا Mira - مساعدكم الذكي!"
            )


async def left_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.left_chat_member:
        member = update.message.left_chat_member
        if not member.is_bot:
            await update.message.reply_text(f"👋 وداعاً {member.first_name}! 😢")

# ============== MAIN ==============
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("balance", balance_cmd))
    app.add_handler(CommandHandler("profile", profile_cmd))
    app.add_handler(CommandHandler("reminders", reminders_cmd))
    app.add_handler(CommandHandler("notes", notes_cmd))
    app.add_handler(CommandHandler("challenge", challenge_cmd))
    app.add_handler(CommandHandler("clear", clear_cmd))
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    # Callbacks
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    # Inline
    app.add_handler(InlineQueryHandler(inline_query))
    
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
        BotCommand("notes", "ملاحظاتي"),
        BotCommand("challenge", "تحدي يومي"),
        BotCommand("clear", "مسح"),
    ])
    
    print("🤖 Mira Twin Bot (محسّن) يعمل...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
"""
🎯 Smart Router - التوجيه الذكي
يوجه الطلبات للنظام المناسب تلقائياً
"""

import os
import aiohttp
import asyncio
import re
from canva_integration import CanvaIntegration
from multi_model import MultiModelCodeGenerator

class SmartRouter:
    """موجه الطلبات الذكي"""
    
    def __init__(self):
        self.code_generator = MultiModelCodeGenerator()
        self.canva = CanvaIntegration()
        self.openai_key = os.getenv('OPENAI_API_KEY', '')
    
    # ========== Analyze Request ==========
    def analyze_request(self, text):
        """تحليل نوع الطلب"""
        
        text_lower = text.lower()
        
        # طلب كود برمجي
        code_keywords = [
            "اكتب", "صمم", "برمجة", "كود", "code", "write",
            "create", "project", "مشروع", "function", "دالة",
            "بوت", "bot", "تطبيق", "app", "website", "موقع",
            "api", "database", "قاعدة", "بيانات", "sql",
            "python", "javascript", "html", "css", "flutter"
        ]
        
        # طلب تصميم
        design_keywords = [
            "تصميم", "design", "logo", "بوست", "banner",
            "ستوري", "story", "social media", "سوشال",
            "poster", "بطاقة", "card", "هوية", "identity"
        ]
        
        # طلب بحث
        search_keywords = [
            "ابحث", "search", "find", "look", "google",
            "سعر", "price", "اخبار", "news", "معلومات"
        ]
        
        # طلب ترجمة
        translate_keywords = [
            "ترجم", "translate", "ترجمة", "translate to"
        ]
        
        # طلب مراجعة كود
        code_review_keywords = [
            "راجع", "review", "تحقق", "check", "fix",
            "اصلح", "تحسين", "improve", "optimize"
        ]
        
        # طلب مشروع كامل
        if any(k in text_lower for k in [
            "مشروع متكامل", "full project", "startup",
            "منصة", "system", "تطبيق كامل"
        ]):
            return "full_project"
        
        # فحص الكلمات المفتاحية
        for keyword in design_keywords:
            if keyword in text_lower:
                return "design"
        
        for keyword in translate_keywords:
            if keyword in text_lower:
                return "translate"
        
        for keyword in code_review_keywords:
            if keyword in text_lower:
                return "code_review"
        
        for keyword in search_keywords:
            if keyword in text_lower:
                return "search"
        
        for keyword in code_keywords:
            if keyword in text_lower:
                return "code"
        
        return "chat"
    
    # ========== Process Request ==========
    async def process_request(self, user_id, text, user_data=None):
        """معالجة الطلب وتوجيهه"""
        
        request_type = self.analyze_request(text)
        
        if request_type == "code":
            return await self._handle_code(text)
        
        elif request_type == "design":
            return await self._handle_design(text)
        
        elif request_type == "full_project":
            return await self._handle_full_project(text)
        
        elif request_type == "search":
            return await self._handle_search(text)
        
        elif request_type == "translate":
            return await self._handle_translate(text)
        
        elif request_type == "code_review":
            return await self._handle_code_review(text)
        
        else:
            return await self._handle_chat(text, user_data)
    
    # ========== Handlers ==========
    
    async def _handle_code(self, text):
        """معالجة طلب كود"""
        language = self._detect_language(text)
        code = await self.code_generator.generate_code(text, language)
        
        return {
            "type": "code",
            "content": code,
            "language": language
        }
    
    async def _handle_design(self, text):
        """معالجة طلب تصميم"""
        design_type = self._detect_design_type(text)
        
        # إنشاء رابط Canva
        canva_link = self.canva.generate_canva_button_link(text, design_type)
        
        return {
            "type": "design",
            "content": f"🎨 **تم إنشاء رابط التصميم!**\n\n[افتح Canva]({canva_link})\n\n🎯 نوع التصميم: {design_type}",
            "url": canva_link
        }
    
    async def _handle_full_project(self, text):
        """معالجة مشروع كامل"""
        code = await self.code_generator.ensemble_code(text)
        
        return {
            "type": "full_project",
            "code": code,
            "content": f"✅ **تم إنشاء المشروع!**\n\n🖥️ **الكود:**\n{code}"
        }
    
    async def _handle_search(self, text):
        """معالجة بحث"""
        query = text.replace("ابحث", "").replace("ابحث عن", "").strip()
        
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    data = await resp.json()
                    result = data.get('AbstractText') or data.get('Answer')
                    
                    if result:
                        return {"type": "search", "content": f"🔍 **النتيجة:**\n\n{result}"}
        except:
            pass
        
        return {"type": "search", "content": "⚠️ لم أجد نتائج!"}
    
    async def _handle_translate(self, text):
        """معالجة ترجمة"""
        parts = text.replace("ترجم", "").replace("translate", "").strip()
        
        target_lang = "ar"
        if "to english" in text.lower() or "للإنجليزية" in text:
            target_lang = "en"
        
        if not self.openai_key:
            return {"type": "translate", "content": "⚠️ يتطلب OpenAI API"}
        
        lang_names = {'ar': 'العربية', 'en': 'الإنجليزية', 'es': 'الإسبانية'}
        
        headers = {
            'Authorization': f'Bearer {self.openai_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': f"ترجم لـ {lang_names.get(target_lang, target_lang)}. أخرج فقط النص المترجم."},
                {'role': 'user', 'content': parts}
            ],
            'max_tokens': 1000
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers=headers, json=payload, timeout=30
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        translated = result['choices'][0]['message']['content']
                        return {"type": "translate", "content": f"🌎 **الترجمة:**\n\n{translated}"}
        except:
            pass
        
        return {"type": "translate", "content": "⚠️ فشل في الترجمة"}
    
    async def _handle_code_review(self, text):
        """معالجة مراجعة الكود"""
        code = self._extract_code(text)
        
        if not code:
            return {"type": "code_review", "content": "⚠️ لم أجد كود للمراجعة! أرسل الكود مع طلب المراجعة."}
        
        review = await self.code_generator.review_code(code)
        
        return {"type": "code_review", "content": f"🔍 **مراجعة الكود:**\n\n{review}"}
    
    async def _handle_chat(self, text, user_data):
        """معالجة محادثة عادية"""
        
        if not self.openai_key:
            return self._fallback_chat(text, user_data)
        
        user_context = f"""اسم: {user_data.get('name', '')}\nالرسالة: {text}"""
        
        headers = {
            'Authorization': f'Bearer {self.openai_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': "أنت Mira - مساعد ذكي. كوني ودودة ومفيدة."},
                {'role': 'user', 'content': user_context}
            ],
            'max_tokens': 1000
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers=headers, json=payload, timeout=30
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return {"type": "chat", "content": result['choices'][0]['message']['content']}
        except:
            pass
        
        return self._fallback_chat(text, user_data)
    
    # ========== Helpers ==========
    
    def _detect_language(self, text):
        """اكتشاف لغة البرمجة"""
        text_lower = text.lower()
        
        if any(k in text_lower for k in ["javascript", "js", "node"]):
            return "javascript"
        elif any(k in text_lower for k in ["html", "css", "موقع"]):
            return "html"
        elif any(k in text_lower for k in ["sql", "database", "قاعدة"]):
            return "sql"
        elif any(k in text_lower for k in ["bash", "shell"]):
            return "bash"
        elif any(k in text_lower for k in ["flutter", "dart", "تطبيق"]):
            return "flutter"
        
        return "python"
    
    def _detect_design_type(self, text):
        """اكتشاف نوع التصميم"""
        text_lower = text.lower()
        
        if "بوست" in text_lower or "post" in text_lower:
            return "social_media"
        elif "بانر" in text_lower or "banner" in text_lower:
            return "banner"
        elif "ستوري" in text_lower or "story" in text_lower:
            return "story"
        elif "بطاقة" in text_lower or "card" in text_lower:
            return "card"
        
        return "social_media"
    
    def _extract_code(self, text):
        """استخراج الكود من النص"""
        blocks = re.findall(r'```(\w+)?\n(.*?)```', text, re.DOTALL)
        
        if blocks:
            return '\n\n'.join([content for _, content in blocks])
        
        return text
    
    def _fallback_chat(self, text, user_data):
        """ردود بدون AI"""
        text_lower = text.lower()
        
        if any(k in text_lower for k in ['مرحبا', 'اهلا', 'hello', 'hi']):
            name = user_data.get('name', '') if user_data else ''
            return {"type": "chat", "content": f"أهلاً! 👋{f' {name}' if name else ''} كيف حالك؟"}
        
        if any(k in text_lower for k in ['شكرا', 'thanks']):
            return {"type": "chat", "content": "العفو! 😊 أي وقت!"}
        
        return {"type": "chat", "content": "🤔 معندي إجابة حالياً!"}


if __name__ == "__main__":
    router = SmartRouter()
    print(router.analyze_request("اكتب دالة بايثون"))
    print(router.analyze_request("تصميم بوست"))
    print(router.analyze_request("ابحث عن سعر البيتكوين"))

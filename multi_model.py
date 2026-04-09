"""
🤖 Multi-Model Code Generator - نماذج برمجة متعددة
يدعم: GPT-4, GPT-3.5, Claude, Gemini, CodeLlama
"""

import os
import aiohttp
import asyncio
import anthropic

class MultiModelCodeGenerator:
    """مولد أكواد متعدد النماذج"""
    
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY', '')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
        self.google_key = os.getenv('GOOGLE_API_KEY', '')
        self.cohere_key = os.getenv('COHERE_API_KEY', '')
    
    # ========== Model Selection ==========
    def select_model(self, prompt, language="python"):
        """اختيار النموذج المناسب حسب نوع الطلب"""
        
        prompt_lower = prompt.lower()
        
        # مشاريع معقدة ومتعددة الملفات
        if any(k in prompt_lower for k in [
            "مشروع متكامل", "full project", "system", "architecture",
            "database", "api", "microservice", "منصة", "تطبيق كامل"
        ]):
            return "gpt-4"
        
        # كود إبداعي ومبتكر
        if any(k in prompt_lower for k in [
            "creative", "unique", "innovative", "mvp",
            "prototype", "game", "لعبة", "animation", "animate",
            "creative", "مبتكر", "ألعاب"
        ]):
            return "claude"
        
        # بحث وتوثيق وشرح
        if any(k in prompt_lower for k in [
            "explain", "شرح", "document", "توثيق",
            "tutorial", "درس", "learn", "شرح", "كيف", "طريقة"
        ]):
            return "gemini"
        
        # كود متخصص (CodeLlama)
        if any(k in prompt_lower for k in [
            "code only", "كود فقط", "function", "دالة",
            "algorithm", "خوارزمية", "optimize", "تحسين"
        ]):
            return "codelama"
        
        # كود بسيط - الافتراضي
        return "gpt-3.5-turbo"
    
    # ========== All Models ==========
    
    async def use_gpt4(self, prompt, language="python"):
        """GPT-4 للمشاريع المعقدة"""
        if not self.openai_key:
            return self._fallback_message("OpenAI")
        
        language_names = {
            'python': 'Python', 'javascript': 'JavaScript', 'html': 'HTML/CSS',
            'sql': 'SQL', 'bash': 'Bash', 'flutter': 'Flutter',
            'java': 'Java', 'c': 'C', 'cpp': 'C++', 'go': 'Go',
            'rust': 'Rust', 'ruby': 'Ruby', 'php': 'PHP'
        }
        
        system_prompt = f"""أنت مبرمج محترف.
اكتب كود {language_names.get(language, language)} كامل ومُشتغل.

المتطلبات:
1. هيكل الملفات كامل
2. كل ملف بالكود الكامل
3. تعليقات مفصلة بالعربية
4. معالجة الأخطاء
5. أمثلة استخدام
6. متطلبات التشغيل

أخرج الكود في ```code blocks``` مع تحديد اللغة"""
        
        headers = {
            'Authorization': f'Bearer {self.openai_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'gpt-4-turbo',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 8000,
            'temperature': 0.7
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers=headers, json=payload, timeout=120
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result['choices'][0]['message']['content']
                    else:
                        return f"❌ خطأ: {await resp.text()}"
        except Exception as e:
            return f"❌ خطأ: {str(e)}"
    
    async def use_gpt35(self, prompt, language="python"):
        """GPT-3.5 للكود البسيط"""
        if not self.openai_key:
            return self._fallback_message("OpenAI")
        
        language_names = {
            'python': 'Python', 'javascript': 'JavaScript', 'html': 'HTML',
            'sql': 'SQL', 'bash': 'Bash', 'flutter': 'Flutter'
        }
        
        system_prompt = f"""اكتب كود {language_names.get(language, language)} نظيف ومُوثق.
الكود يكون كامل ومُشتغل.
أضف تعليقات بالعربية.
أخرج في ```code blocks```"""
        
        headers = {
            'Authorization': f'Bearer {self.openai_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 2000,
            'temperature': 0.7
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers=headers, json=payload, timeout=60
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result['choices'][0]['message']['content']
                    else:
                        return f"❌ خطأ: {await resp.text()}"
        except Exception as e:
            return f"❌ خطأ: {str(e)}"
    
    async def use_claude(self, prompt, language="python"):
        """Claude للإبداع والتحليل"""
        if not self.anthropic_key:
            return self._fallback_message("Anthropic")
        
        try:
            client = anthropic.Anthropic(api_key=self.anthropic_key)
            
            language_names = {
                'python': 'Python', 'javascript': 'JavaScript', 'html': 'HTML/CSS',
                'sql': 'SQL', 'bash': 'Bash', 'flutter': 'Flutter'
            }
            
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4000,
                system=f"""أنت مبرمج مبدع ومحترف.
اكتب كود {language_names.get(language, language)} إبداعي ومبتكر.
فكر خارج الصندوق.
قدم حلولاً فريدة ومبتكرة.
الكود يكون كامل ومُشتغل مع أفضل الممارسات.
أضف تعليقات مفصلة.
أخرج الكود في ```code blocks```""",
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
        except Exception as e:
            return f"❌ خطأ: {str(e)}"
    
    async def use_gemini(self, prompt, language="python"):
        """Gemini للبحث والتوثيق"""
        if not self.google_key:
            return self._fallback_message("Google")
        
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={self.google_key}"
        
        language_names = {
            'python': 'Python', 'javascript': 'JavaScript', 'html': 'HTML',
            'sql': 'SQL', 'bash': 'Bash', 'flutter': 'Flutter'
        }
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"اكتب كود {language_names.get(language, language)} لـ: {prompt}"
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 4000
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result['candidates'][0]['content']['parts'][0]['text']
                    else:
                        return f"❌ خطأ: {await resp.text()}"
        except Exception as e:
            return f"❌ خطأ: {str(e)}"
    
    # ========== Main Generator ==========
    async def generate_code(self, prompt, language="python"):
        """توليد كود بالنموذج المناسب"""
        
        model = self.select_model(prompt, language)
        
        if model == "gpt-4":
            return await self.use_gpt4(prompt, language)
        elif model == "claude":
            return await self.use_claude(prompt, language)
        elif model == "gemini":
            return await self.use_gemini(prompt, language)
        elif model == "codelama":
            return "⚠️ يتطلب Cohere API"
        else:
            return await self.use_gpt35(prompt, language)
    
    # ========== Ensemble (Voting) ==========
    async def ensemble_code(self, prompt, language="python"):
        """تصويت من عدة نماذج واختيار الأفضل"""
        
        tasks = [
            self.use_gpt35(prompt, language),
            self.use_claude(prompt, language),
            self.use_gemini(prompt, language)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # تصفية النتائج
        valid_results = [r for r in results if isinstance(r, str) and not r.startswith('❌')]
        
        if not valid_results:
            return "⚠️ فشل في توليد الكود من جميع النماذج"
        
        # اختيار الأفضل (الأطول والأكثر تفصيلاً)
        best = max(valid_results, key=lambda x: len(x))
        
        return best
    
    # ========== Helpers ==========
    def _fallback_message(self, provider):
        return f"⚠️ **{provider} API غير مُفعَّل**\n\nأضف المفتاح في متغير البيئة المناسب."
    
    # ========== Code Review ==========
    async def review_code(self, code, language="python"):
        """مراجعة الكود"""
        
        if not self.openai_key:
            return "⚠️ يتطلب OpenAI API"
        
        headers = {
            'Authorization': f'Bearer {self.openai_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'gpt-4-turbo',
            'messages': [
                {'role': 'system', 'content': "أنت مبرمج ومراجع كود. راجع الكود واقترح تحسينات. أجب بالعربية."},
                {'role': 'user', 'content': f"مراجعة كود {language}:\n{code}"}
            ],
            'max_tokens': 2000
        }
        
        try:
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
        
        return "⚠️ فشل في مراجعة الكود"


if __name__ == "__main__":
    asyncio.run(MultiModelCodeGenerator().generate_code("اكتب دالة بايثون", "python"))

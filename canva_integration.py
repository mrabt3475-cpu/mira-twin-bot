"""
🎨 Canva Integration - ربط Canva للتصميم
تتيح إنشاء تصاميم وتصديرها برمجياً
"""

import os
import json
import aiohttp
import base64
import asyncio
from datetime import datetime

class CanvaIntegration:
    """تكامل مع Canva API"""
    
    def __init__(self):
        self.canva_api_key = os.getenv('CANVA_API_KEY', '')
        self.canva_client_id = os.getenv('CANVA_CLIENT_ID', '')
        self.canva_client_secret = os.getenv('CANVA_CLIENT_SECRET', '')
        self.access_token = None
        self.refresh_token = None
    
    # ========== OAuth Authentication ==========
    def get_auth_url(self):
        """الحصول على رابط التوثيق"""
        if not self.canva_client_id:
            return None, "⚠️ مطلوب Canva Client ID"
        
        redirect_uri = os.getenv('CANVA_REDIRECT_URI', 'https://yourbot.com/callback')
        auth_url = (
            f"https://www.canva.com/api/oauth/authorize?"
            f"client_id={self.canva_client_id}&"
            f"response_type=code&"
            f"redirect_uri={redirect_uri}&"
            f"scope=design:read design:write design:content:read"
        )
        return auth_url, "✅"
    
    async def exchange_code_for_token(self, code):
        """تبادل الكود للوصول"""
        token_url = "https://api.canva.com/rest/v1/oauth/token"
        
        auth = base64.b64encode(
            f"{self.canva_client_id}:{self.canva_client_secret}".encode()
        ).decode()
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': os.getenv('CANVA_REDIRECT_URI'),
            'client_id': self.canva_client_id
        }
        
        headers = {
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(token_url, data=data, headers=headers) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        self.access_token = result.get('access_token')
                        self.refresh_token = result.get('refresh_token')
                        return result, "✅ تم التوثيق!"
                    else:
                        return None, "❌ فشل التوثيق"
        except Exception as e:
            return None, f"❌ خطأ: {str(e)}"
    
    # ========== Design Creation ==========
    async def create_design(self, design_type="social_media", title="تصميم جديد"):
        """إنشاء تصميم جديد"""
        if not self.access_token:
            return None, "⚠️ غير مُوثَّق! استخدم get_auth_url() أولاً"
        
        url = "https://api.canva.com/rest/v1/designs"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        design_types = {
            'social_media': 'social_media',
            'presentation': 'presentation',
            'poster': 'poster',
            'banner': 'banner',
            'story': 'story',
            'logo': 'logo',
            'card': 'card'
        }
        
        data = {
            "design": {
                "type": design_types.get(design_type, 'social_media'),
                "title": title
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as resp:
                    if resp.status == 201:
                        result = await resp.json()
                        return result, "✅ تم إنشاء التصميم!"
                    else:
                        error = await resp.text()
                        return None, f"❌ خطأ: {error}"
        except Exception as e:
            return None, f"❌ خطأ: {str(e)}"
    
    # ========== Add Elements ==========
    async def add_text(self, design_id, text, x=100, y=100, font_size=24, color="#000000"):
        """إضافة نص للتصميم"""
        if not self.access_token:
            return None, "⚠️ غير مُوثَّق!"
        
        url = f"https://api.canva.com/rest/v1/designs/{design_id}/elements"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "type": "text",
            "content": text,
            "position": {"x": x, "y": y},
            "style": {
                "fontSize": font_size,
                "color": color
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as resp:
                    if resp.status in [200, 201]:
                        return await resp.json(), "✅ تم إضافة النص!"
                    else:
                        return None, f"❌ خطأ: {await resp.text()}"
        except Exception as e:
            return None, f"❌ خطأ: {str(e)}"
    
    async def add_image(self, design_id, image_url, x=100, y=100, width=200, height=200):
        """إضافة صورة للتصميم"""
        if not self.access_token:
            return None, "⚠️ غير مُوثَّق!"
        
        url = f"https://api.canva.com/rest/v1/designs/{design_id}/elements"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "type": "image",
            "url": image_url,
            "position": {"x": x, "y": y},
            "size": {"width": width, "height": height}
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as resp:
                    if resp.status in [200, 201]:
                        return await resp.json(), "✅ تم إضافة الصورة!"
                    else:
                        return None, f"❌ خطأ: {await resp.text()}"
        except Exception as e:
            return None, f"❌ خطأ: {str(e)}"
    
    # ========== Export Design ==========
    async def export_design(self, design_id, format="png", quality="high"):
        """تصدير التصميم"""
        if not self.access_token:
            return None, "⚠️ غير مُوثَّق!"
        
        url = f"https://api.canva.com/rest/v1/designs/{design_id}/export"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "format": format,
            "quality": quality,
            "pages": [1]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as resp:
                    if resp.status == 202:
                        result = await resp.json()
                        export_id = result.get('export', {}).get('id')
                        return await self.wait_for_export(export_id)
                    else:
                        return None, f"❌ خطأ: {await resp.text()}"
        except Exception as e:
            return None, f"❌ خطأ: {str(e)}"
    
    async def wait_for_export(self, export_id, max_wait=30):
        """انتظار اكتمال التصدير"""
        url = f"https://api.canva.com/rest/v1/exports/{export_id}"
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        for _ in range(max_wait):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            export = result.get('export', {})
                            
                            if export.get('status') == 'success':
                                return export.get('download_url'), "✅ تم التصدير!"
                            elif export.get('status') == 'failed':
                                return None, "❌ فشل التصدير"
                            
                            await asyncio.sleep(2)
            except:
                pass
        
        return None, "⏰ انتهت مهلة الانتظار"
    
    # ========== Quick Design Functions ==========
    async def create_social_post(self, title, subtitle, background_color="#1a1a2e", text_color="#ffffff"):
        """إنشاء بوست سوشال ميديا سريع"""
        
        design, msg = await self.create_design("social_media", title)
        if not design:
            return None, msg
        
        design_id = design.get('design', {}).get('id')
        
        await self.add_shape(design_id, "rectangle", 0, 0, 1080, 1080, background_color)
        await self.add_text(design_id, title, 100, 200, 48, text_color)
        await self.add_text(design_id, subtitle, 100, 400, 24, text_color)
        
        return await self.export_design(design_id)
    
    async def create_banner(self, title, subtitle, background_color="#16213e", text_color="#e94560"):
        """إنشاء بانر"""
        
        design, msg = await self.create_design("banner", title)
        if not design:
            return None, msg
        
        design_id = design.get('design', {}).get('id')
        
        await self.add_shape(design_id, "rectangle", 0, 0, 1920, 600, background_color)
        await self.add_text(design_id, title, 100, 200, 60, text_color)
        await self.add_text(design_id, subtitle, 100, 400, 30, text_color)
        
        return await self.export_design(design_id)


def generate_canva_button_link(text, design_type="social_media"):
    """إنشاء رابط Canva Button للتصميم"""
    
    canva_button_url = (
        f"https://www.canva.com/design/create?"
        f"type={design_type}&"
        f"title={text}"
    )
    
    return canva_button_url


if __name__ == "__main__":
    import asyncio
    canva = CanvaIntegration()
    print(canva.get_auth_url())

"""
🏪 Shop System - نظام المتجر
بيع منتجات وخدمات
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ShopSystem:
    """نظام المتجر"""
    
    def __init__(self, data_file='mira_data.json'):
        self.data_file = data_file
        self._init_shop()
    
    def _init_shop(self):
        """تهيئة المتجر"""
        if not os.path.exists(self.data_file):
            data = {"shop": {"items": []}}
            self.save_data(data)
        else:
            data = self.load_data()
            if 'shop' not in data:
                data['shop'] = {'items': []}
                self.save_data(data)
    
    def load_data(self) -> dict:
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"shop": {"items": []}}
    
    def save_data(self, data: dict):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ========== Items Management ==========
    
    def add_item(self, item_id: str, name: str, price: int, item_type: str, 
                 amount: int = 1, description: str = "", duration: int = None,
                 image_url: str = "", features: List[str] = None) -> bool:
        """إضافة منتج"""
        
        data = self.load_data()
        
        # التحقق من وجود المنتج
        for item in data['shop']['items']:
            if item['id'] == item_id:
                return False
        
        item = {
            "id": item_id,
            "name": name,
            "price": price,
            "type": item_type,  # images, points, subscription, project, custom
            "amount": amount,
            "description": description,
            "duration": duration,
            "image_url": image_url,
            "features": features or [],
            "active": True,
            "created_at": datetime.now().isoformat()
        }
        
        data['shop']['items'].append(item)
        self.save_data(data)
        
        return True
    
    def update_item(self, item_id: str, **kwargs) -> bool:
        """تحديث منتج"""
        
        data = self.load_data()
        
        for item in data['shop']['items']:
            if item['id'] == item_id:
                item.update(kwargs)
                self.save_data(data)
                return True
        
        return False
    
    def delete_item(self, item_id: str) -> bool:
        """حذف منتج"""
        
        data = self.load_data()
        
        data['shop']['items'] = [
            item for item in data['shop']['items'] 
            if item['id'] != item_id
        ]
        
        self.save_data(data)
        return True
    
    def get_item(self, item_id: str) -> Optional[dict]:
        """جلب منتج"""
        
        data = self.load_data()
        
        for item in data['shop']['items']:
            if item['id'] == item_id:
                return item
        
        return None
    
    def get_all_items(self, item_type: str = None) -> List[dict]:
        """جلب كل المنتجات"""
        
        data = self.load_data()
        items = data['shop']['items']
        
        if item_type:
            items = [i for i in items if i.get('type') == item_type and i.get('active', True)]
        else:
            items = [i for i in items if i.get('active', True)]
        
        return items
    
    # ========== Categories ==========
    
    def get_categories(self) -> Dict[str, List[dict]]:
        """جلب الفئات"""
        
        items = self.get_all_items()
        categories = {}
        
        for item in items:
            item_type = item.get('type', 'other')
            if item_type not in categories:
                categories[item_type] = []
            categories[item_type].append(item)
        
        return categories
    
    def get_category_name(self, item_type: str) -> str:
        """اسم الفئة"""
        
        names = {
            "images": "🎨 الصور",
            "points": "💎 النقاط",
            "subscription": "⭐️ الاشتراكات",
            "project": "🖥️ المشاريع",
            "custom": "🎯 مخصص",
            "game": "🎮 ألعاب",
            "vip": "👑 VIP"
        }
        
        return names.get(item_type, item_type)
    
    # ========== Display Shop ==========
    
    def display_shop(self, item_type: str = None) -> str:
        """عرض المتجر"""
        
        if item_type:
            items = self.get_all_items(item_type)
            return self._format_items(items, self.get_category_name(item_type))
        
        # عرض كل الفئات
        categories = self.get_categories()
        
        if not categories:
            return "🏪 المتجر فارغ حالياً"
        
        text = "🏪 **المتجر:**\n\n"
        
        for item_type, items in categories.items():
            text += f"{self.get_category_name(item_type)}\n"
            text += self._format_items(items, "")
            text += "\n"
        
        return text
    
    def _format_items(self, items: List[dict], category_name: str) -> str:
        """تنسيق المنتجات"""
        
        if not items:
            return ""
        
        text = ""
        if category_name:
            text = f"\n📦 **{category_name}:**\n"
        
        for item in items:
            text += f"• **{item['name']}** - {item['price']} نقطة"
            
            if item.get('amount') and item['amount'] > 1:
                text += f" ({item['amount']})"
            
            if item.get('duration'):
                text += f" - {item['duration']} يوم"
            
            text += "\n"
        
        return text
    
    # ========== Purchase ==========
    
    def purchase(self, user_id: int, item_id: str) -> tuple:
        """شراء منتج"""
        
        from points_system import PointsSystem
        
        points = PointsSystem(self.data_file)
        
        # جلب المنتج
        item = self.get_item(item_id)
        
        if not item:
            return False, "المنتج غير موجود"
        
        if not item.get('active', True):
            return False, "المنتج غير متاح"
        
        # التحقق من الرصيد
        balance = points.get_balance(user_id)
        
        if balance < item['price']:
            return False, f"رصيدك: {balance} - المطلوب: {item['price']}"
        
        # خصم النقاط
        success, msg = points.deduct_points(
            user_id, 
            item['price'], 
            f"شراء: {item['name']}"
        )
        
        if not success:
            return False, msg
        
        # تفعيل المنتج
        self._activate_purchase(user_id, item)
        
        return True, f"✅ تم شراء {item['name']}!"
    
    def _activate_purchase(self, user_id: int, item: dict):
        """تفعيل المنتج"""
        
        from points_system import PointsSystem
        
        points = PointsSystem(self.data_file)
        data = points.load_data()
        uid = str(user_id)
        
        if 'purchases' not in data['users'][uid]:
            data['users'][uid]['purchases'] = []
        
        purchase = {
            "item_id": item['id'],
            "name": item['name'],
            "type": item['type'],
            "amount": item.get('amount', 1),
            "purchased_at": datetime.now().isoformat()
        }
        
        # إذا كان اشتراك
        if item['type'] == 'subscription':
            days = item.get('duration', 30)
            expires = (datetime.now() + timedelta(days=days)).isoformat()
            data['users'][uid]['premium'] = True
            data['users'][uid]['subscription_type'] = item['id']
            data['users'][uid]['subscription_expires'] = expires
            purchase['expires'] = expires
        
        # إذا كان نقاط
        elif item['type'] == 'points':
            points.add_points(user_id, item.get('amount', 0), f"شحن نقاط: {item['name']}")
        
        data['users'][uid]['purchases'].append(purchase)
        points.save_data(data)
    
    # ========== User Purchases ==========
    
    def get_user_purchases(self, user_id: int) -> List[dict]:
        """مشتريات المستخدم"""
        
        from points_system import PointsSystem
        
        points = PointsSystem(self.data_file)
        user = points.get_user(user_id)
        
        if not user:
            return []
        
        return user.get('purchases', [])
    
    def get_active_purchases(self, user_id: int) -> List[dict]:
        """المشتريات النشطة"""
        
        purchases = self.get_user_purchases(user_id)
        active = []
        
        for p in purchases:
            if p.get('type') == 'subscription':
                expires = p.get('expires')
                if expires and datetime.fromisoformat(expires) > datetime.now():
                    active.append(p)
            else:
                active.append(p)
        
        return active
    
    # ========== Admin ==========
    
    def get_shop_stats(self) -> dict:
        """إحصائيات المتجر"""
        
        from points_system import PointsSystem
        
        points = PointsSystem(self.data_file)
        items = self.get_all_items()
        
        total_sales = 0
        total_revenue = 0
        
        for user in points.get_all_users():
            purchases = user.get('purchases', [])
            total_sales += len(purchases)
            
            for p in purchases:
                item = self.get_item(p.get('item_id', ''))
                if item:
                    total_revenue += item.get('price', 0)
        
        return {
            "total_items": len(items),
            "total_sales": total_sales,
            "total_revenue": total_revenue
        }


# ========== Initialize Default Shop ==========

def init_default_shop():
    """تهيئة المتجر الافتراضي"""
    
    shop = ShopSystem()
    
    # الصور
    shop.add_item(
        "10_images", "10 صور", 30, "images", 10,
        "10 صور مولدة بالذكاء الاصطناعي",
        features=["جودة عالية", "بدون علامة مائية"]
    )
    
    shop.add_item(
        "50_images", "50 صورة", 120, "images", 50,
        "50 صورة مولدة بالذكاء الاصطناعي",
        features=["جودة عالية", "بدون علامة مائية", "أولوية"]
    )
    
    shop.add_item(
        "100_images", "100 صورة", 200, "images", 100,
        "100 صورة مولدة بالذكاء الاصطناعي",
        features=["جودة عالية", "بدون علامة مائية", "أولوية", "دعم فني"]
    )
    
    # النقاط
    shop.add_item(
        "100_points", "100 نقطة", 30, "points", 100,
        "شحن 100 نقطة"
    )
    
    shop.add_item(
        "500_points", "500 نقطة", 120, "points", 550,
        "شحن 500 نقطة + 50 بونص",
        features=["بونص 10%"]
    )
    
    shop.add_item(
        "1000_points", "1000 نقطة", 200, "points", 1200,
        "شحن 1000 نقطة + 200 بونص",
        features=["بونص 20%"]
    )
    
    # الاشتراكات
    shop.add_item(
        "pro_month", "Mira Pro - شهر", 500, "subscription", 1,
        "اشتراك Pro لمدة شهر", duration=30,
        features=["بدون علامة مائية", "أولوية", "دعم فني", "جودة عالية"]
    )
    
    shop.add_item(
        "pro_year", "Mira Pro - سنة", 4500, "subscription", 1,
        "اشتراك Pro لمدة سنة", duration=365,
        features=["بدون علامة مائية", "أولوية", "دعم فني", "جودة عالية", "20% خصم"]
    )
    
    # المشاريع
    shop.add_item(
        "custom_project", "مشروع مخصص", 200, "project", 1,
        "إنشاء مشروع برمجي مخصص",
        features=["كود كامل", "توثيق", "دعم"]
    )
    
    shop.add_item(
        "bot_telegram", "بوت تليجرام", 300, "project", 1,
        "بوت تليجرام متكامل",
        features=["كود كامل", "لوحة تحكم", "قاعدة بيانات"]
    )
    
    shop.add_item(
        "website_portfolio", "موقع portfolio", 400, "project", 1,
        "موقع شخصي احترافي",
        features=["تصميم حديث", "متجاوب", "SEO"]
    )
    
    print("✅ تم تهيئة المتجر الافتراضي")


if __name__ == "__main__":
    init_default_shop()
    
    shop = ShopSystem()
    print(shop.display_shop())

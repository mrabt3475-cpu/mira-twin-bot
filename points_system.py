"""
💰 Points & Payments System - نظام النقاط والدفع
نظام إحالة، عمولة، نقاط، ومتجر بيع
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class PointsSystem:
    """نظام النقاط"""
    
    def __init__(self, data_file='mira_data.json'):
        self.data_file = data_file
        self._init_data()
    
    def _init_data(self):
        """تهيئة قاعدة البيانات"""
        if not os.path.exists(self.data_file):
            default_data = {
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
                "commissions": {}
            }
            self.save_data(default_data)
    
    def load_data(self) -> dict:
        """تحميل البيانات"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"users": {}, "shop": {"items": []}, "daily_rewards": {}, "referrals": {}, "commissions": {}}
    
    def save_data(self, data: dict):
        """حفظ البيانات"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ========== User Management ==========
    
    def create_user(self, user_id: int, name: str = "", username: str = "") -> dict:
        """إنشاء مستخدم جديد"""
        data = self.load_data()
        uid = str(user_id)
        
        if uid not in data['users']:
            data['users'][uid] = {
                "name": name,
                "username": username,
                "balance": 0,
                "premium": False,
                "subscription_type": None,
                "subscription_expires": None,
                "transactions": [],
                "purchases": [],
                "xp": 0,
                "level": 1,
                "referral_code": self._generate_referral_code(),
                "referred_by": None,
                "referral_count": 0,
                "total_earned": 0,
                "total_spent": 0,
                "created_at": datetime.now().isoformat(),
                "last_daily": None,
                "streak": 0
            }
            self.save_data(data)
        
        return data['users'][uid]
    
    def _generate_referral_code(self) -> str:
        """إنشاء كود إحالة فريد"""
        import random
        import string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def get_user(self, user_id: int) -> Optional[dict]:
        """جلب بيانات مستخدم"""
        data = self.load_data()
        return data['users'].get(str(user_id))
    
    # ========== Points Operations ==========
    
    def add_points(self, user_id: int, amount: int, reason: str, referrer_id: int = None) -> tuple:
        """إضافة نقاط"""
        data = self.load_data()
        uid = str(user_id)
        
        if uid not in data['users']:
            self.create_user(user_id)
            data = self.load_data()
        
        # إضافة النقاط
        data['users'][uid]['balance'] += amount
        data['users'][uid]['total_earned'] += amount
        
        # تسجيل المعاملة
        data['users'][uid]['transactions'].append({
            "type": "earn",
            "amount": amount,
            "description": reason,
            "date": datetime.now().isoformat()
        })
        
        # تحديث XP
        self._add_xp(user_id, amount)
        
        # إذا كان هناك مُحيل، أعطِ عمولة
        if referrer_id:
            self._give_referral_commission(referrer_id, amount)
        
        self.save_data(data)
        return True, data['users'][uid]['balance']
    
    def deduct_points(self, user_id: int, amount: int, reason: str) -> tuple:
        """خصم نقاط"""
        data = self.load_data()
        uid = str(user_id)
        
        if uid not in data['users']:
            return False, "المستخدم غير موجود"
        
        current_balance = data['users'][uid].get('balance', 0)
        
        if current_balance < amount:
            return False, f"رصيد غير كافٍ. الرصيد: {current_balance}"
        
        data['users'][uid]['balance'] -= amount
        data['users'][uid]['total_spent'] += amount
        
        data['users'][uid]['transactions'].append({
            "type": "spend",
            "amount": -amount,
            "description": reason,
            "date": datetime.now().isoformat()
        })
        
        self.save_data(data)
        return True, data['users'][uid]['balance']
    
    def get_balance(self, user_id: int) -> int:
        """عرض الرصيد"""
        user = self.get_user(user_id)
        return user.get('balance', 0) if user else 0
    
    # ========== XP & Levels ==========
    
    def _add_xp(self, user_id: int, points: int):
        """إضافة XP وتحديث المستوى"""
        data = self.load_data()
        uid = str(user_id)
        
        xp_gained = points // 2  # كل نقطتين = 1 XP
        data['users'][uid]['xp'] = data['users'][uid].get('xp', 0) + xp_gained
        
        # حساب المستوى الجديد
        xp = data['users'][uid]['xp']
        new_level = 1 + int(xp ** 0.5)  # مستوى جديد لكل 1، 4، 9، 16... XP
        
        if new_level > data['users'][uid].get('level', 1):
            data['users'][uid]['level'] = new_level
            data['users'][uid]['transactions'].append({
                "type": "level_up",
                "amount": 0,
                "description": f"🎉 ترقية للمستوى {new_level}!",
                "date": datetime.now().isoformat()
            })
        
        self.save_data(data)
    
    def get_level(self, user_id: int) -> int:
        """جلب المستوى"""
        user = self.get_user(user_id)
        return user.get('level', 1) if user else 1
    
    def get_xp(self, user_id: int) -> int:
        """جلب XP"""
        user = self.get_user(user_id)
        return user.get('xp', 0) if user else 0
    
    def get_xp_for_next_level(self, user_id: int) -> int:
        """XP المطلوب للمستوى التالي"""
        level = self.get_level(user_id)
        return (level + 1) ** 2
    
    # ========== Referral System ==========
    
    def get_referral_code(self, user_id: int) -> str:
        """جلب كود الإحالة"""
        user = self.get_user(user_id)
        return user.get('referral_code', '') if user else ''
    
    def use_referral_code(self, user_id: int, referral_code: str) -> tuple:
        """استخدام كود إحالة"""
        data = self.load_data()
        uid = str(user_id)
        
        # البحث عن صاحب كود الإحالة
        referrer_id = None
        for uid_check, user_data in data['users'].items():
            if user_data.get('referral_code') == referral_code:
                referrer_id = int(uid_check)
                break
        
        if not referrer_id:
            return False, "كود الإحالة غير صالح"
        
        if referrer_id == user_id:
            return False, "لا يمكنك استخدام كود الإحالة الخاص بك"
        
        # تحديث بيانات المُحال
        if uid not in data['users']:
            self.create_user(user_id)
            data = self.load_data()
        
        if data['users'][uid].get('referred_by'):
            return False, "لديك بالفعل مُحيل"
        
        # تعيين المُحيل
        data['users'][uid]['referred_by'] = referrer_id
        data['users'][uid]['referral_count'] = 0
        
        # تحديث عدّاد المُحيل
        data['users'][str(referrer_id)]['referral_count'] = data['users'][str(referrer_id)].get('referral_count', 0) + 1
        
        # منح مكافأة الإحالة
        referral_bonus = 50
        data['users'][uid]['balance'] += referral_bonus
        data['users'][str(referrer_id)]['balance'] += referral_bonus
        
        # تسجيل المعاملات
        data['users'][uid]['transactions'].append({
            "type": "referral_bonus",
            "amount": referral_bonus,
            "description": "مكافأة التسجيل عبر إحالة",
            "date": datetime.now().isoformat()
        })
        
        data['users'][str(referrer_id)]['transactions'].append({
            "type": "referral_commission",
            "amount": referral_bonus,
            "description": f"عمولة إحالة: مستخدم جديد",
            "date": datetime.now().isoformat()
        })
        
        self.save_data(data)
        return True, f"✅ تم تفعيل الإحالة! حصلت على {referral_bonus} نقطة"
    
    def _give_referral_commission(self, referrer_id: int, points: int):
        """منح عمولة للمُحيل"""
        commission_rate = 0.10  # 10% عمولة
        commission = int(points * commission_rate)
        
        if commission > 0:
            data = self.load_data()
            rid = str(referrer_id)
            
            if rid in data['users']:
                data['users'][rid]['balance'] += commission
                data['users'][rid]['transactions'].append({
                    "type": "referral_commission",
                    "amount": commission,
                    "description": f"عمولة 10% من نقاط {points}",
                    "date": datetime.now().isoformat()
                })
                
                self.save_data(data)
    
    def get_referral_stats(self, user_id: int) -> dict:
        """إحصائيات الإحالة"""
        user = self.get_user(user_id)
        if not user:
            return {}
        
        return {
            "referral_count": user.get('referral_count', 0),
            "total_earned": user.get('total_earned', 0),
            "referral_code": user.get('referral_code', '')
        }
    
    # ========== Daily Rewards ==========
    
    def claim_daily_reward(self, user_id: int) -> tuple:
        """المطالبة بالمكافأة اليومية"""
        data = self.load_data()
        uid = str(user_id)
        
        if uid not in data['users']:
            self.create_user(user_id)
            data = self.load_data()
        
        user = data['users'][uid]
        last_claim = user.get('last_daily')
        today = datetime.now().date()
        
        if last_claim:
            last_date = datetime.fromisoformat(last_claim).date()
            if last_date == today:
                return False, "⚠️你已经 طالبت بمكافأتك اليومية اليوم!"
            
            # التحقق من التتابع
            if (today - last_date).days == 1:
                user['streak'] = user.get('streak', 0) + 1
            else:
                user['streak'] = 1
        else:
            user['streak'] = 1
        
        # حساب المكافأة
        streak = user['streak']
        base_reward = 10
        bonus = min(streak * 2, 50)  # بونص حتى 50
        reward = base_reward + bonus
        
        user['balance'] += reward
        user['last_daily'] = datetime.now().isoformat()
        
        user['transactions'].append({
            "type": "daily_reward",
            "amount": reward,
            "description": f"مكافأة يومية (سلسلة: {streak} أيام)",
            "date": datetime.now().isoformat()
        })
        
        self.save_data(data)
        return True, f"✅ مكافأة يومية: {reward} نقطة! (سلسلة: {streak} أيام 🔥)"
    
    # ========== Shop ==========
    
    def get_shop_items(self) -> List[dict]:
        """جلب عناصر المتجر"""
        data = self.load_data()
        return data.get('shop', {}).get('items', [])
    
    def buy_item(self, user_id: int, item_id: str) -> tuple:
        """شراء منتج"""
        data = self.load_data()
        uid = str(user_id)
        
        if uid not in data['users']:
            self.create_user(user_id)
            data = self.load_data()
        
        # البحث عن المنتج
        item = None
        for shop_item in data['shop']['items']:
            if shop_item['id'] == item_id:
                item = shop_item
                break
        
        if not item:
            return False, "المنتج غير موجود"
        
        current_balance = data['users'][uid].get('balance', 0)
        
        if current_balance < item['price']:
            return False, f"رصيدك: {current_balance} - المطلوب: {item['price']}"
        
        # خصم النقاط
        data['users'][uid]['balance'] -= item['price']
        data['users'][uid]['total_spent'] += item['price']
        
        # تفعيل المنتج
        if 'purchases' not in data['users'][uid]:
            data['users'][uid]['purchases'] = []
        
        purchase = {
            "item_id": item['id'],
            "name": item['name'],
            "type": item['type'],
            "amount": item.get('amount', 1),
            "activated": datetime.now().isoformat()
        }
        
        # إذا كان اشتراك
        if item['type'] == 'subscription':
            days = item.get('duration', 30)
            expires = (datetime.now() + timedelta(days=days)).isoformat()
            data['users'][uid]['premium'] = True
            data['users'][uid]['subscription_type'] = item['id']
            data['users'][uid]['subscription_expires'] = expires
            purchase['expires'] = expires
        
        data['users'][uid]['purchases'].append(purchase)
        
        # تسجيل المعاملة
        data['users'][uid]['transactions'].append({
            "type": "purchase",
            "amount": -item['price'],
            "description": f"شراء: {item['name']}",
            "date": datetime.now().isoformat()
        })
        
        self.save_data(data)
        return True, f"✅ تم شراء {item['name']}!"
    
    # ========== Transactions ==========
    
    def get_transactions(self, user_id: int, limit: int = 10) -> List[dict]:
        """سجل المعاملات"""
        user = self.get_user(user_id)
        if not user:
            return []
        
        transactions = user.get('transactions', [])
        return sorted(transactions, key=lambda x: x['date'], reverse=True)[:limit]
    
    # ========== Admin Functions ==========
    
    def add_points_admin(self, user_id: int, amount: int, reason: str = "إضافة من الأدمن") -> bool:
        """إضافة نقاط من الأدمن"""
        success, _ = self.add_points(user_id, amount, reason)
        return success
    
    def remove_points_admin(self, user_id: int, amount: int, reason: str = "خصم من الأدمن") -> bool:
        """خصم نقاط من الأدمن"""
        success, _ = self.deduct_points(user_id, amount, reason)
        return success
    
    def get_all_users(self) -> List[dict]:
        """جلب كل المستخدمين"""
        data = self.load_data()
        return [
            {"id": int(uid), **user_data} 
            for uid, user_data in data['users'].items()
        ]
    
    def get_stats(self) -> dict:
        """إحصائيات عامة"""
        data = self.load_data()
        users = data['users']
        
        total_users = len(users)
        total_balance = sum(u.get('balance', 0) for u in users.values())
        total_spent = sum(u.get('total_spent', 0) for u in users.values())
        total_earned = sum(u.get('total_earned', 0) for u in users.values())
        premium_users = sum(1 for u in users.values() if u.get('premium'))
        
        return {
            "total_users": total_users,
            "total_balance": total_balance,
            "total_spent": total_spent,
            "total_earned": total_earned,
            "premium_users": premium_users
        }


# ========== Payment System (TON/Crypto) ==========

class PaymentSystem:
    """نظام الدفع"""
    
    def __init__(self, points_system: PointsSystem):
        self.points = points_system
        self.ton_wallet = os.getenv('TON_WALLET_ADDRESS', '')
        self.admin_id = os.getenv('ADMIN_ID', '')
    
    async def create_invoice(self, user_id: int, amount: float, currency: str = "TON") -> dict:
        """إنشاء فاتورة"""
        
        invoice_id = f"inv_{user_id}_{int(datetime.now().timestamp())}"
        
        # هنا يتم إنشاء فاتورة حقيقية عبر TON API
        # مثال توضيحي:
        
        invoice = {
            "invoice_id": invoice_id,
            "user_id": user_id,
            "amount": amount,
            "currency": currency,
            "wallet_address": self.ton_wallet,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
        }
        
        return invoice
    
    async def verify_payment(self, invoice_id: str, tx_hash: str) -> tuple:
        """التحقق من الدفع"""
        
        # هنا يتم التحقق من transaction على البلوكتشين
        # مثال:
        
        # محاكاة التحقق
        verified = True
        amount_received = 1.0  # TON
        
        if verified:
            return True, {
                "verified": True,
                "amount_received": amount_received,
                "status": "completed"
            }
        
        return False, {"verified": False, "status": "failed"}
    
    async def process_payment(self, user_id: int, item_id: str, tx_hash: str) -> tuple:
        """معالجة الدفع"""
        
        # التحقق من الدفع
        verified, payment_data = await self.verify_payment(tx_hash, "")
        
        if not verified:
            return False, "فشل في التحقق من الدفع"
        
        # تحويل للدفع إلى نقاط
        # 1 TON = 1000 نقطة
        points_earned = int(payment_data['amount_received'] * 1000)
        
        # إضافة النقاط
        self.points.add_points(user_id, points_earned, f"شحن عبر TON: {tx_hash[:10]}...")
        
        return True, f"✅ تم إضافة {points_earned} نقطة!"
    
    def get_payment_link(self, user_id: int, amount: float) -> str:
        """رابط الدفع"""
        
        # رابط الدفع عبر Telegram
        return f"https://t.me/{self.ton_wallet}?amount={int(amount * 1e9)}"


# ========== Example Usage ==========

if __name__ == "__main__":
    points = PointsSystem()
    
    # إنشاء مستخدم
    points.create_user(123456, "أحمد", "ahmed_user")
    
    # إضافة نقاط
    points.add_points(123456, 100, "مكافأة يومية")
    
    # عرض الرصيد
    print(f"الرصيد: {points.get_balance(123456)}")
    
    # عرض المستوى
    print(f"المستوى: {points.get_level(123456)}")
    
    # كود الإحالة
    print(f"كود الإحالة: {points.get_referral_code(123456)}")
    
    # استخدام كود إحالة
    points.create_user(789012, "محمد", "mohamed_user")
    result, msg = points.use_referral_code(789012, points.get_referral_code(123456))
    print(msg)
    
    # شراء منتج
    result, msg = points.buy_item(123456, "100_points")
    print(msg)
    
    # إحصائيات
    print(points.get_stats())

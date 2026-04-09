"""
🎁 Referral System - نظام الإحالة
إحالة، عمولات، ومكافآت
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ReferralSystem:
    """نظام الإحالة المتقدم"""
    
    def __init__(self, data_file='mira_data.json'):
        self.data_file = data_file
        self.commission_rate = 0.10  # 10% عمولة
        self.referral_bonus = 50  # نقاط مكافأة التسجيل
        self.max_referrals = 100  # الحد الأقصى للمُحيلين
    
    def load_data(self) -> dict:
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"users": {}, "referrals": {}}
    
    def save_data(self, data: dict):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ========== Referral Code ==========
    
    def generate_code(self, user_id: int) -> str:
        """إنشاء كود إحالة فريد"""
        import random
        import string
        
        # كود مختصر من 6 أحرف
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # إضافة بادئة من اسم المستخدم
        data = self.load_data()
        uid = str(user_id)
        if uid in data['users']:
            name = data['users'][uid].get('name', '')
            if name:
                code = name[:3].upper() + code
        
        return code
    
    def get_referral_link(self, user_id: int, bot_username: str = "mira") -> str:
        """رابط الإحالة"""
        code = self.get_referral_code(user_id)
        return f"https://t.me/{bot_username}?start=ref_{code}"
    
    def get_referral_code(self, user_id: int) -> str:
        """جلب كود الإحالة"""
        data = self.load_data()
        uid = str(user_id)
        
        if uid in data['users']:
            return data['users'][uid].get('referral_code', '')
        
        return ''
    
    # ========== Process Referral ==========
    
    def process_referral(self, new_user_id: int, referral_code: str) -> tuple:
        """معالجة إحالة جديدة"""
        data = self.load_data()
        new_uid = str(new_user_id)
        
        # البحث عن صاحب الكود
        referrer_id = None
        for uid, user_data in data['users'].items():
            if user_data.get('referral_code') == referral_code:
                referrer_id = int(uid)
                break
        
        if not referrer_id:
            return False, "كود الإحالة غير صالح", None
        
        if referrer_id == new_user_id:
            return False, "لا يمكنك استخدام كودك الخاص", None
        
        # التحقق من عدم وجود إحالة سابقة
        if new_uid in data['users']:
            if data['users'][new_uid].get('referred_by'):
                return False, "لديك بالفعل مُحيل", None
        
        # التحقق من حد الإحالة
        referrer_data = data['users'].get(str(referrer_id), {})
        if referrer_data.get('referral_count', 0) >= self.max_referrals:
            return False, "المُحيل وصل للحد الأقصى", None
        
        # تفعيل الإحالة
        if new_uid not in data['users']:
            data['users'][new_uid] = {
                "balance": 0,
                "transactions": []
            }
        
        # تعيين المُحيل
        data['users'][new_uid]['referred_by'] = referrer_id
        data['users'][new_uid]['referral_count'] = 0
        data['users'][new_uid]['referral_activated'] = datetime.now().isoformat()
        
        # تحديث عدّاد المُحيل
        if str(referrer_id) not in data['users']:
            data['users'][str(referrer_id)] = {"referral_count": 0}
        
        data['users'][str(referrer_id)]['referral_count'] = \
            data['users'][str(referrer_id)].get('referral_count', 0) + 1
        
        # منح المكافآت
        # للمُحال
        data['users'][new_uid]['balance'] = \
            data['users'][new_uid].get('balance', 0) + self.referral_bonus
        
        # للمُحيل
        data['users'][str(referrer_id)]['balance'] = \
            data['users'][str(referrer_id)].get('balance', 0) + self.referral_bonus
        
        # تسجيل المعاملات
        data['users'][new_uid]['transactions'].append({
            "type": "referral_bonus",
            "amount": self.referral_bonus,
            "description": "مكافأة التسجيل عبر إحالة",
            "date": datetime.now().isoformat()
        })
        
        data['users'][str(referrer_id)]['transactions'].append({
            "type": "referral_commission",
            "amount": self.referral_bonus,
            "description": f"عمولة إحالة: مستخدم جديد",
            "date": datetime.now().isoformat()
        })
        
        self.save_data(data)
        
        return True, f"✅ تم تفعيل الإحالة!

🎁 المكافآت:
• أنت: +{self.referral_bonus} نقطة
• المُحيل: +{self.referral_bonus} نقطة", referrer_id
    
    # ========== Commission ==========
    
    def give_commission(self, referrer_id: int, points_earned: int) -> int:
        """منح عمولة للمُحيل"""
        
        commission = int(points_earned * self.commission_rate)
        
        if commission > 0:
            data = self.load_data()
            rid = str(referrer_id)
            
            if rid in data['users']:
                data['users'][rid]['balance'] = \
                    data['users'][rid].get('balance', 0) + commission
                
                data['users'][rid]['transactions'].append({
                    "type": "referral_commission",
                    "amount": commission,
                    "description": f"عمولة 10% من {points_earned} نقطة",
                    "date": datetime.now().isoformat()
                })
                
                # تحديث إجمالي العمولات
                data['users'][rid]['total_commissions'] = \
                    data['users'][rid].get('total_commissions', 0) + commission
                
                self.save_data(data)
        
        return commission
    
    # ========== Stats ==========
    
    def get_referrer_stats(self, user_id: int) -> dict:
        """إحصائيات المُحيل"""
        data = self.load_data()
        uid = str(user_id)
        
        if uid not in data['users']:
            return {}
        
        user = data['users'][uid]
        
        return {
            "referral_code": user.get('referral_code', ''),
            "referral_count": user.get('referral_count', 0),
            "total_commissions": user.get('total_commissions', 0),
            "max_referrals": self.max_referrals
        }
    
    def get_referred_users(self, user_id: int) -> List[dict]:
        """جلب قائمة المُحيلين"""
        data = self.load_data()
        
        referred = []
        for uid, user_data in data['users'].items():
            if user_data.get('referred_by') == user_id:
                referred.append({
                    "id": int(uid),
                    "name": user_data.get('name', ''),
                    "username": user_data.get('username', ''),
                    "joined": user_data.get('referral_activated', ''),
                    "balance": user_data.get('balance', 0)
                })
        
        return referred
    
    def get_top_referrers(self, limit: int = 10) -> List[dict]:
        """أفضل المُحيلين"""
        data = self.load_data()
        
        referrers = []
        for uid, user_data in data['users'].items():
            count = user_data.get('referral_count', 0)
            if count > 0:
                referrers.append({
                    "id": int(uid),
                    "name": user_data.get('name', ''),
                    "username": user_data.get('username', ''),
                    "referral_count": count,
                    "total_commissions": user_data.get('total_commissions', 0)
                })
        
        # ترتيب حسب عدد الإحالات
        referrers.sort(key=lambda x: x['referral_count'], reverse=True)
        
        return referrers[:limit]
    
    # ========== Leaderboard ==========
    
    def get_referral_leaderboard(self) -> str:
        """لوحة المتصدرين"""
        
        top = self.get_top_referrers(10)
        
        if not top:
            return "📊 لا يوجد مُحيلين بعد"
        
        text = "🏆 **أفضل المُحيلين:**\n\n"
        
        medals = ["🥇", "🥈", "🥉"]
        
        for i, user in enumerate(top):
            medal = medals[i] if i < 3 else f"{i+1}."
            name = user.get('name') or user.get('username') or f"مستخدم {user['id']}"
            text += f"{medal} **{name}**\n"
            text += f"   👥 {user['referral_count']} إحالة\n"
            text += f"   💰 {user.get('total_commissions', 0)} نقطة\n\n"
        
        return text


# ========== Commission Tiers ==========

class CommissionTier:
    """نظام مستويات العمولات"""
    
    TIERS = {
        "bronze": {
            "name": "برونزي",
            "min_referrals": 0,
            "commission_rate": 0.10,
            "bonus": 0
        },
        "silver": {
            "name": "فضي",
            "min_referrals": 10,
            "commission_rate": 0.12,
            "bonus": 100
        },
        "gold": {
            "name": "ذهبي",
            "min_referrals": 25,
            "commission_rate": 0.15,
            "bonus": 500
        },
        "platinum": {
            "name": "بلاتيني",
            "min_referrals": 50,
            "commission_rate": 0.20,
            "bonus": 2000
        },
        "diamond": {
            "name": "ماسي",
            "min_referrals": 100,
            "commission_rate": 0.25,
            "bonus": 5000
        }
    }
    
    @classmethod
    def get_tier(cls, referral_count: int) -> dict:
        """جلب المستوى الحالي"""
        
        for tier_name, tier_data in cls.TIERS.items():
            if referral_count >= tier_data['min_referrals']:
                return {
                    "name": tier_data['name'],
                    "rate": tier_data['commission_rate'],
                    "bonus": tier_data['bonus'],
                    "tier": tier_name
                }
        
        return cls.TIERS["bronze"]
    
    @classmethod
    def get_next_tier(cls, current_tier: str) -> dict:
        """جلب المستوى التالي"""
        
        tier_order = ["bronze", "silver", "gold", "platinum", "diamond"]
        
        try:
            current_index = tier_order.index(current_tier)
            if current_index < len(tier_order) - 1:
                next_tier = tier_order[current_index + 1]
                return cls.TIERS[next_tier]
        except:
            pass
        
        return None
    
    @classmethod
    def check_tier_upgrade(cls, user_id: int) -> tuple:
        """التحقق من ترقية المستوى"""
        
        from points_system import PointsSystem
        
        points = PointsSystem()
        stats = points.get_referral_stats(user_id)
        
        referral_count = stats.get('referral_count', 0)
        current_tier = cls.get_tier(referral_count)
        
        # التحقق من الترقية
        for tier_name, tier_data in cls.TIERS.items():
            if referral_count >= tier_data['min_referrals']:
                if tier_name != current_tier.get('tier', 'bronze'):
                    # ترقية!
                    return True, f"🎉 ترقية إلى {tier_data['name']}!\n"
                           f"عمولتك الآن: {int(tier_data['commission_rate']*100)}%"
        
        return False, ""


if __name__ == "__main__":
    ref = ReferralSystem()
    
    # إنشاء أكواد إحالة
    print("كود إحالة:", ref.generate_code(123456))
    print("رابط الإحالة:", ref.get_referral_link(123456))
    
    # معالجة إحالة
    result, msg, _ = ref.process_referral(789012, "REF123")
    print(msg)
    
    # لوحة المتصدرين
    print(ref.get_referral_leaderboard())
    
    # مستويات العمولات
    print(CommissionTier.get_tier(15))

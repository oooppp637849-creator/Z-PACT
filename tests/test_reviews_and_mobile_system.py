import unittest
import os
import re
from fastapi.testclient import TestClient

from app.models import Base, User, UserRole, Material, Purchase, PurchaseStatus, Review
from app.database import SessionLocal, get_db
import app.database as app_db
from app.crud import hash_password
from app.auth import create_access_token
from main import app


class TestReviewsAndMobileSystem(unittest.TestCase):
    """
    اختبارات شاملة ومخصصة لنظام المراجعات والتقييمات وواجهة الموبايل
    """
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_review_api_validation_and_flow(self):
        """التحقق من صحة منطق الـ Backend للتقييمات بالمعايير الثلاثة"""
        admin = self.db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin:
            admin = User(
                full_name="المدير العام",
                email="admin_test_rev@test.com",
                password_hash=hash_password("adminpass"),
                role=UserRole.ADMIN
            )
            self.db.add(admin)
            self.db.commit()

        import uuid
        uid = uuid.uuid4().hex[:6]
        # إنشاء مشتري ومادة
        buyer = User(
            full_name="الأستاذ طارق خليل",
            email=f"tareq_{uid}@test.com",
            phone=f"010{uid[:8]}",
            password_hash=hash_password("TareqPass123!"),
            role=UserRole.CUSTOMER,
            coins=100.0
        )
        material = Material(
            title="مذكرة الإبداع في الرياضيات",
            uploaded_by=admin.id,
            price=20.0,
            price_coins=20.0,
            original_pdf_path="storage/originals/math.pdf",
            total_pages=40,
            is_published=True
        )
        self.db.add_all([buyer, material])
        self.db.commit()

        token = create_access_token(user_id=buyer.id, role=buyer.role.value)
        headers = {"Authorization": f"Bearer {token}"}

        # 1. محاولة إضافة تقييم بقيم غير صالحة (خارج نطاق 1-5)
        bad_payload = {
            "reviewer_title": "معلم أول",
            "content_quality_rating": 6,  # غير صالح
            "print_formatting_rating": 0,  # غير صالح
            "stamp_appearance_rating": 4,
            "comment": "تجربة"
        }
        res_bad = self.client.post(f"/api/materials/{material.id}/reviews", json=bad_payload, headers=headers)
        self.assertEqual(res_bad.status_code, 422)

        # 2. محاولة إضافة تقييم صالح قبل الشراء (403 Forbidden)
        valid_payload = {
            "reviewer_title": "مدرس أول رياضيات",
            "content_quality_rating": 5,
            "print_formatting_rating": 5,
            "stamp_appearance_rating": 4,
            "comment": "مذكرة ممتازة وتنسيق رائع والختم احترافي جداً"
        }
        res_forbidden = self.client.post(f"/api/materials/{material.id}/reviews", json=valid_payload, headers=headers)
        self.assertEqual(res_forbidden.status_code, 403)

        # 3. إتمام عملية الشراء بنجاح
        purchase = Purchase(
            buyer_id=buyer.id,
            material_id=material.id,
            buyer_name_stamp="الأستاذ طارق خليل",
            buyer_phone_stamp="01011223344",
            amount_paid=20.0,
            status=PurchaseStatus.COMPLETED
        )
        self.db.add(purchase)
        self.db.commit()

        # 4. إضافة التقييم بنجاح بعد الشراء
        res_success = self.client.post(f"/api/materials/{material.id}/reviews", json=valid_payload, headers=headers)
        self.assertEqual(res_success.status_code, 200)
        review_data = res_success.json()
        self.assertEqual(review_data["reviewer_name"], "الأستاذ طارق خليل")
        self.assertEqual(review_data["reviewer_title"], "مدرس أول رياضيات")
        expected_overall = round((5 + 5 + 4) / 3.0, 2)
        self.assertEqual(review_data["overall_rating"], expected_overall)

        # 5. استرجاع قائمة التقييمات للمادة والتحقق من حساب المتوسطات
        res_list = self.client.get(f"/api/materials/{material.id}/reviews")
        self.assertEqual(res_list.status_code, 200)
        list_data = res_list.json()
        self.assertEqual(list_data["total_count"], 1)
        self.assertEqual(list_data["avg_content_quality"], 5.0)
        self.assertEqual(list_data["avg_print_formatting"], 5.0)
        self.assertEqual(list_data["avg_stamp_appearance"], 4.0)
        self.assertEqual(list_data["avg_overall"], round((5 + 5 + 4) / 3.0, 1))

    def test_02_store_html_dom_elements(self):
        """التحقق من وجود وتكامل كافة عناصر واجهة الموبايل والتقييمات في store.html"""
        store_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "pages", "store.html")
        with open(store_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. شريط التنقل السفلي العائم مع الوجهات الـ 5
        self.assertIn('id="mobile-bottom-nav"', content)
        self.assertIn('id="btn-nav-store"', content)
        self.assertIn('id="btn-nav-purchases"', content)
        self.assertIn('id="btn-nav-wallet"', content)
        self.assertIn('id="btn-nav-notifs"', content)
        self.assertIn('id="btn-nav-settings"', content)
        self.assertIn('id="bottom-nav-notif-badge"', content)

        # 2. هيدر الموبايل الأصلي (Mobile Sticky Header)
        self.assertIn('id="mobile-sticky-header"', content)
        self.assertIn('class="mobile-brand-pill"', content)
        self.assertIn('id="mobile-avatar-circle"', content)
        self.assertIn('class="mobile-coin-chip"', content)
        self.assertIn('class="mobile-notif-btn"', content)

        # 3. لوحة ملخص التقييمات والأشرطة الثلاثة
        self.assertIn('class="review-dashboard"', content)
        self.assertIn('id="avg-rating"', content)
        self.assertIn('id="avg-stars-display"', content)
        self.assertIn('id="reviews-total-count"', content)
        self.assertIn('id="metric-content-bar"', content)
        self.assertIn('id="metric-print-bar"', content)
        self.assertIn('id="metric-stamp-bar"', content)

        # 4. نافذة التقييم التفاعلية بالنجوم والألقاب
        self.assertIn('id="review-modal"', content)
        self.assertIn('data-metric="content"', content)
        self.assertIn('data-metric="print"', content)
        self.assertIn('data-metric="stamp"', content)
        self.assertIn('star-interactive-btn', content)
        self.assertIn('title-chip-btn', content)
        self.assertIn('id="comment-char-count"', content)
        self.assertIn('id="submit-review-btn"', content)

        # 5. النوافذ المنبثقة من الأسفل (Bottom Sheets) والشريط العائم للمعاينة
        self.assertIn('class="bottom-sheet-handle"', content)
        self.assertIn('id="preview-mobile-sticky-bar"', content)
        self.assertIn('id="mobile-notifications-modal"', content)

        # 6. تفاعلات السحب والاهتزاز اللمسي والتحديث
        self.assertIn('setupSwipeToDismiss', content)
        self.assertIn('triggerHaptic', content)
        self.assertIn('pull-refresh-box', content)

    def test_03_global_css_rules(self):
        """التحقق من قواعد الـ CSS للعزل التام بين شاشات الكمبيوتر والموبايل"""
        css_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "css", "global.css")
        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()

        # التحقق من عزل الكمبيوتر (إخفاء عناصر الموبايل على الشاشات الكبيرة)
        self.assertIn('@media (min-width: 769px)', content)
        self.assertIn('#mobile-bottom-nav', content)
        self.assertIn('#preview-mobile-sticky-bar', content)

        # التحقق من إعدادات الموبايل (عرض البطاقات والهيدر وشريط التنقل)
        self.assertIn('@media (max-width: 768px)', content)
        self.assertIn('.bottom-nav', content)
        self.assertIn('.bottom-nav.nav-hidden', content)
        self.assertIn('.bottom-sheet-handle', content)
        self.assertIn('.mobile-sticky-action-bar', content)
        self.assertIn('.material-card', content)


if __name__ == "__main__":
    unittest.main()

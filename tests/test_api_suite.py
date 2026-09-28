# ================================================================
# tests/test_api_suite.py — حزمة الاختبارات الشاملة لنظام Z-PACT
#
# تغطي هذه الحزمة:
#   1. دورة التوثيق وتسجيل الدخول والتسجيل
#   2. اختبارات الأمان وحماية الصلاحيات (منع ثغرة IDOR في المشتريات)
#   3. إدارة وتتبع الأجهزة وبصمة المتصفح والحد الأقصى
#   4. أمان العملات وصلاحيات لوحة التحكم
#   5. استخراج وتضمين العلامة المائية غير المرئية (DCT Steganography)
#   6. دوال التنسيق للمدرسين وأرقام الهواتف
# ================================================================

import os
import sys
import tempfile
import unittest
import numpy as np
import cv2

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, User, UserRole, Material, Purchase, LayoutType, StampLayout, PurchaseStatus
from app.database import get_db
import app.database as app_db
from app.crud import hash_password
from app.auth import create_access_token
from app.formatting import format_instructor_name, format_contact_phone, clean_phone_number
from app.stamper import _get_smart_text
from app.watermark_dct import embed_dct_watermark, extract_dct_watermark
from main import app


class TestZPACTComprehensiveSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory for isolated test database
        try:
            cls.test_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        except TypeError:
            cls.test_dir = tempfile.TemporaryDirectory()

        cls.test_db_path = os.path.join(cls.test_dir.name, "test_z_pact.db")
        cls.test_engine = create_engine(
            f"sqlite:///{cls.test_db_path}",
            connect_args={"check_same_thread": False}
        )
        cls.TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=cls.test_engine
        )

        # Build schema
        Base.metadata.create_all(bind=cls.test_engine)

        # Patch app_db.SessionLocal
        cls.original_session_local = app_db.SessionLocal
        app_db.SessionLocal = cls.TestingSessionLocal

        # Override get_db dependency
        def override_get_db():
            db = cls.TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

        # Seed initial admin user
        with cls.TestingSessionLocal() as db:
            admin_user = User(
                email="admin_primary@example.com",
                password_hash=hash_password("adminSecret123!"),
                full_name="المدير العام للمنصة",
                role=UserRole.ADMIN,
                is_active=True,
                coins=9999
            )
            db.add(admin_user)
            db.commit()

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()
        app_db.SessionLocal = cls.original_session_local
        cls.test_engine.dispose()
        try:
            cls.test_dir.cleanup()
        except Exception:
            pass

    def setUp(self):
        self.db = self.TestingSessionLocal()

    def tearDown(self):
        self.db.close()

    # -------------------------------------------------------------
    # 1. اختبارات التوثيق وتسجيل الدخول
    # -------------------------------------------------------------
    def test_01_authentication_flow(self):
        """تسجيل حساب جديد ثم تسجيل الدخول والتحقق من التوكن"""
        # 1. تسجيل طالب جديد
        reg_payload = {
            "email": "student_alpha@example.com",
            "password": "SecurePassword123!",
            "full_name": "أحمد الطالب الأول"
        }
        res_reg = self.client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(res_reg.status_code, 201, f"Registration failed: {res_reg.text}")
        data = res_reg.json()
        self.assertEqual(data["email"], "student_alpha@example.com")
        self.assertEqual(data["role"], "customer")

        # 2. تكرار التسجيل بنفس الإيميل يجب أن يعيد 400
        res_dup = self.client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(res_dup.status_code, 400)

        # 3. تسجيل الدخول بكلمة مرور خاطئة -> 401
        res_bad_pw = self.client.post(
            "/api/auth/login",
            json={
                "email": "student_alpha@example.com",
                "password": "WrongPassword!",
                "device_id": "device_101"
            }
        )
        self.assertEqual(res_bad_pw.status_code, 401)

        # 4. تسجيل الدخول ببيانات صحيحة -> 200 + access_token
        res_login = self.client.post(
            "/api/auth/login",
            json={
                "email": "student_alpha@example.com",
                "password": "SecurePassword123!",
                "device_id": "device_101"
            },
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        self.assertEqual(res_login.status_code, 200)
        login_data = res_login.json()
        self.assertIn("access_token", login_data)
        self.assertEqual(login_data["user"]["email"], "student_alpha@example.com")

    # -------------------------------------------------------------
    # 2. اختبارات الأمان وحماية الصلاحيات (IDOR Protection)
    # -------------------------------------------------------------
    def test_02_purchase_idor_security(self):
        """
        التحقق الصارم من حماية تفاصيل الشراء ضد تسريب IDOR:
        - المستخدم A يملك العملية.
        - المستخدم B يحاول استعراض تفاصيل العملية -> يجب أن يحصل على 403 Forbidden.
        - المدير (Admin) مسموح له باستعراض تفاصيل العملية.
        """
        # إنشاء مستخدم A ومستخدم B
        pw_hash = hash_password("pass12345")
        user_a = User(
            email="buyer_a@example.com",
            password_hash=pw_hash,
            full_name="مشتري أ",
            role=UserRole.CUSTOMER,
            is_active=True,
            coins=100
        )
        user_b = User(
            email="buyer_b@example.com",
            password_hash=pw_hash,
            full_name="مشتري ب",
            role=UserRole.CUSTOMER,
            is_active=True,
            coins=100
        )
        self.db.add_all([user_a, user_b])
        self.db.commit()
        self.db.refresh(user_a)
        self.db.refresh(user_b)

        admin_user = self.db.query(User).filter(User.role == UserRole.ADMIN).first()

        # إنشاء مذكرة
        material = Material(
            title="مذكرة التفوق في الكيمياء",
            uploaded_by=admin_user.id,
            price=15.0,
            price_coins=15.0,
            original_pdf_path="storage/originals/chem.pdf",
            total_pages=60,
            is_published=True
        )
        self.db.add(material)
        self.db.commit()
        self.db.refresh(material)

        # إنشاء عملية شراء لمستخدم A
        purchase = Purchase(
            buyer_id=user_a.id,
            material_id=material.id,
            buyer_name_stamp="محمود عبد العزيز",
            buyer_phone_stamp="01098765432",
            watermark_text="نسخة مرخصة",
            amount_paid=15.0,
            status="completed"
        )
        self.db.add(purchase)
        self.db.commit()
        self.db.refresh(purchase)

        # توليد JWT Tokens
        token_a = create_access_token(user_id=user_a.id, role=user_a.role.value)
        token_b = create_access_token(user_id=user_b.id, role=user_b.role.value)
        token_admin = create_access_token(user_id=admin_user.id, role=admin_user.role.value)

        # 1. مستخدم A يستعلم عن مشترياته الخاصة -> 200 OK
        res_a = self.client.get(
            f"/api/purchases/{purchase.id}",
            headers={"Authorization": f"Bearer {token_a}"}
        )
        self.assertEqual(res_a.status_code, 200)
        self.assertEqual(res_a.json()["id"], purchase.id)
        self.assertEqual(res_a.json()["buyer_id"], user_a.id)

        # 2. مستخدم B يستعلم عن مشتريات A -> 403 Forbidden لمنع تسريب الـ IDOR
        res_b = self.client.get(
            f"/api/purchases/{purchase.id}",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        self.assertEqual(
            res_b.status_code, 
            403, 
            f"Critical IDOR vulnerability! Expected 403, got {res_b.status_code}"
        )
        self.assertIn("ليس لديك صلاحية", res_b.json().get("detail", ""))

        # 3. المدير يستعلم عن العملية -> 200 OK
        res_admin = self.client.get(
            f"/api/purchases/{purchase.id}",
            headers={"Authorization": f"Bearer {token_admin}"}
        )
        self.assertEqual(res_admin.status_code, 200)
        self.assertEqual(res_admin.json()["id"], purchase.id)

    # -------------------------------------------------------------
    # 3. اختبارات إدارة وتتبع الأجهزة وبصمة المتصفح
    # -------------------------------------------------------------
    def test_03_device_fingerprinting_and_admin_management(self):
        """تسجيل الأجهزة، التحقق من الحظر، وإعادة التعيين بواسطة المسؤول"""
        student = self.db.query(User).filter(User.email == "student_alpha@example.com").first()
        admin = self.db.query(User).filter(User.role == UserRole.ADMIN).first()
        admin_token = create_access_token(user_id=admin.id, role=admin.role.value)

        # استعراض أجهزة الطالب من لوحة الإدارة
        res_devs = self.client.get(
            f"/api/users/admin/{student.id}/devices",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        self.assertEqual(res_devs.status_code, 200)
        devices = res_devs.json()
        self.assertTrue(len(devices) >= 1)
        device_record_id = devices[0]["id"]
        self.assertEqual(devices[0]["device_id"], "device_101")

        # تبديل حالة حظر الجهاز إلى محظور
        res_toggle = self.client.post(
            f"/api/users/admin/devices/{device_record_id}/toggle-block",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        self.assertEqual(res_toggle.status_code, 200)
        self.assertIn("محظور", res_toggle.json()["message"])

        # محاولة الطالب تسجيل الدخول من هذا الجهاز المحظور يجب أن تفشل مع 403
        res_blocked_login = self.client.post(
            "/api/auth/login",
            json={
                "email": "student_alpha@example.com",
                "password": "SecurePassword123!",
                "device_id": "device_101"
            }
        )
        self.assertEqual(res_blocked_login.status_code, 403)
        self.assertIn("محظور", res_blocked_login.json()["detail"])

        # إعادة تعيين وحذف جميع أجهزة الطالب بواسطة الأدمن
        res_reset = self.client.delete(
            f"/api/users/admin/{student.id}/devices",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        self.assertEqual(res_reset.status_code, 200)

        # التحقق من خلو قائمة الأجهزة المسجلة
        res_check = self.client.get(
            f"/api/users/admin/{student.id}/devices",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        self.assertEqual(len(res_check.json()), 0)

    # -------------------------------------------------------------
    # 4. اختبارات أمان العملات وباقات الصرف
    # -------------------------------------------------------------
    def test_04_role_based_access_control(self):
        """التأكد من منع الطلاب من الترقية لمدير أو تعديل باقات الصرف"""
        student = self.db.query(User).filter(User.email == "buyer_a@example.com").first()
        student_token = create_access_token(user_id=student.id, role=student.role.value)
        admin = self.db.query(User).filter(User.role == UserRole.ADMIN).first()
        admin_token = create_access_token(user_id=admin.id, role=admin.role.value)

        # محاولة طالب ترقية مستخدم لمدير
        res_prom = self.client.post(
            f"/api/coins/admin/users/{student.id}/make-admin",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        self.assertEqual(res_prom.status_code, 403)

        # محاولة طالب إضافة باقة صرف
        level_data = {
            "threshold": 300.0,
            "reward_coins": 25.0
        }
        res_lvl_student = self.client.post(
            "/api/coins/admin/spending-levels",
            json=level_data,
            headers={"Authorization": f"Bearer {student_token}"}
        )
        self.assertEqual(res_lvl_student.status_code, 403)

        # المسؤول يمكنه إنشاء الباقة بنجاح
        res_lvl_admin = self.client.post(
            "/api/coins/admin/spending-levels",
            json=level_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        self.assertIn(res_lvl_admin.status_code, [200, 201])

    # -------------------------------------------------------------
    # 5. اختبار العلامة المائية الرقمية غير المرئية (DCT Watermark)
    # -------------------------------------------------------------
    def test_05_dct_steganography_watermark(self):
        """تضمين رقم الشراء داخل مصفوفة التردد واستخراجه بدقة 100%"""
        test_img_path = os.path.join(self.test_dir.name, "test_dct_sample.png")

        # صورة اختبارية 256x256
        img = np.zeros((256, 256, 3), dtype=np.uint8)
        for r in range(256):
            img[r, :, 0] = int(r * 0.9)
            img[r, :, 1] = 140
            img[r, :, 2] = int(255 - r * 0.7)
        cv2.imwrite(test_img_path, img)

        purchase_id_to_hide = 554433

        # تضمين الختم
        embed_dct_watermark(test_img_path, purchase_id_to_hide, delta=16.0)

        # استخراج الختم
        recovered_id = extract_dct_watermark(test_img_path)
        self.assertEqual(
            recovered_id, 
            purchase_id_to_hide, 
            f"DCT extraction failed! Expected {purchase_id_to_hide}, got {recovered_id}"
        )

    # -------------------------------------------------------------
    # 6. اختبارات دوال التنسيق
    # -------------------------------------------------------------
    def test_06_formatting_utilities(self):
        """التحقق من توحيد صيغ الأسماء وأرقام الهواتف"""
        self.assertEqual(format_instructor_name("أ. وائل"), "أ / وائل")
        self.assertEqual(format_instructor_name("الاستاذ وائل"), "أ / وائل")
        self.assertEqual(format_instructor_name("مهندس كريم"), "مهندس كريم")
        self.assertEqual(format_instructor_name("دكتور نبيل"), "دكتور نبيل")
        self.assertEqual(format_contact_phone("01155443322"), "ت / 01155443322")
        self.assertEqual(format_contact_phone("هاتف / 01012345678"), "ت / 01012345678")

        # اختبار استخراج أرقام الهواتف لصفحة الغلاف بدون "ت /" أو "ت \"
        self.assertEqual(clean_phone_number("01012345678"), "01012345678")
        self.assertEqual(clean_phone_number("ت / 01012345678"), "01012345678")
        self.assertEqual(clean_phone_number("ت \\ 01012345678"), "01012345678")
        self.assertEqual(clean_phone_number("ت. 01012345678"), "01012345678")
        self.assertEqual(clean_phone_number("هاتف: 01012345678"), "01012345678")

        # اختبار النصوص الذكية للعلامة المائية واسم المذكرة (كلمة واحدة vs أكثر من كلمة)
        self.assertEqual(_get_smart_text("لا للنشر", "", "الرياضيات"), "لا للنشر")
        self.assertEqual(_get_smart_text("لا للنشر", "سلسلة", "الرياضيات"), "لا للنشر")
        self.assertEqual(_get_smart_text("ممنوع تداول المذكرة", "", "الفيزياء"), "ممنوع تداول المذكرة")
        self.assertEqual(_get_smart_text("تفوق", "سلسلة", "الرياضيات"), "سلسلة تفوق في الرياضيات")
        self.assertEqual(_get_smart_text("تفوق", "", "الرياضيات"), "تفوق في الرياضيات")

    # -------------------------------------------------------------
    # 7. اختبار عمليات الشراء المتتالية وتنسيق صفحة الغلاف
    # -------------------------------------------------------------
    def test_07_repeated_purchases_and_cover_stamp(self):
        """
        التحقق من:
        1. نجاح عمليات الشراء المتتالية لنفس المستخدم دون توقف أو أخطاء تكرار.
        2. ختم صفحة الغلاف برقم الهاتف النقي فقط بدون سوابق.
        """
        pw_hash = hash_password("pass12345")
        buyer = User(
            email="repeat_buyer@example.com",
            password_hash=pw_hash,
            full_name="مشتري مكرر",
            role=UserRole.CUSTOMER,
            is_active=True,
            coins=200
        )
        self.db.add(buyer)
        self.db.commit()
        self.db.refresh(buyer)

        admin_user = self.db.query(User).filter(User.role == UserRole.ADMIN).first()

        import fitz
        dummy_pdf_path = os.path.join(self.test_dir.name, "bio.pdf")
        test_pdf_doc = fitz.open()
        test_pdf_doc.new_page()
        test_pdf_doc.new_page()
        test_pdf_doc.save(dummy_pdf_path)
        test_pdf_doc.close()

        material = Material(
            title="مذكرة الأحياء الثانوية",
            uploaded_by=admin_user.id,
            price=20.0,
            price_coins=20.0,
            original_pdf_path=dummy_pdf_path,
            total_pages=2,
            is_published=True
        )
        self.db.add(material)
        self.db.commit()
        self.db.refresh(material)

        layout = StampLayout(
            material_id=material.id,
            created_by=admin_user.id,
            layout_type=LayoutType.DEFAULT,
            stamp_elements=[
                {"type": "name", "page": 0, "x_pct": 10, "y_pct": 10, "font_size": 12},
                {"type": "phone", "page": 0, "x_pct": 10, "y_pct": 15, "font_size": 12}
            ]
        )
        self.db.add(layout)
        self.db.commit()

        token = create_access_token(user_id=buyer.id, role=buyer.role.value)
        headers = {"Authorization": f"Bearer {token}"}

        # عملية الشراء الأولى (بالكوينز)
        p1_data = {
            "material_id": material.id,
            "buyer_name_stamp": "أحمد إبراهيم",
            "buyer_phone_stamp": "ت / 01011112222",
            "watermark_type": "text",
            "payment_method": "coins",
            "transaction_id": None
        }
        res1 = self.client.post("/api/purchases", json=p1_data, headers=headers)
        self.assertEqual(res1.status_code, 201)

        # عملية الشراء الثانية (لنفس المستخدم - كوينز بدون أي خطأ تعارض)
        p2_data = {
            "material_id": material.id,
            "buyer_name_stamp": "أحمد إبراهيم",
            "buyer_phone_stamp": "01011112222",
            "watermark_type": "text",
            "payment_method": "coins",
            "transaction_id": None
        }
        res2 = self.client.post("/api/purchases", json=p2_data, headers=headers)
        self.assertEqual(res2.status_code, 201)

        # التحقق من خصم الكوينز للمرتين (40 كوينز)
        self.db.refresh(buyer)
        self.assertEqual(float(buyer.coins), 160.0)

        # التحقق من أن رقم الهاتف على الغلاف يستخرج نقياً
        raw_phone_input = "ت \\ 01011112222"
        cover_phone = clean_phone_number(raw_phone_input)
        self.assertEqual(cover_phone, "01011112222")
        self.assertNotIn("ت", cover_phone)
        self.assertNotIn("\\", cover_phone)
        self.assertNotIn("/", cover_phone)

    def test_08_material_reviews_and_ratings(self):
        """اختبار دورة التقييمات والمراجعات: القيود والحسابات والجلب"""
        # 1. إنشاء مستخدم ومادة
        admin_user = self.db.query(User).filter(User.role == UserRole.ADMIN).first()
        reviewer = User(
            full_name="الأستاذ مصطفى كامل",
            email="teacher_mustafa@example.com",
            phone="01099998888",
            password_hash=hash_password("RevPass123!"),
            role=UserRole.CUSTOMER,
            coins=50.0
        )
        material = Material(
            title="مذكرة التفوق في الجيولوجيا",
            uploaded_by=admin_user.id,
            price=15.0,
            price_coins=15.0,
            original_pdf_path="storage/originals/geo.pdf",
            total_pages=30,
            is_published=True
        )
        self.db.add_all([reviewer, material])
        self.db.commit()

        token = create_access_token(user_id=reviewer.id, role=reviewer.role.value)
        headers = {"Authorization": f"Bearer {token}"}

        # 2. جلب التقييمات لمادة جديدة (يجب أن يكون فارغاً)
        res_empty = self.client.get(f"/api/materials/{material.id}/reviews")
        self.assertEqual(res_empty.status_code, 200)
        data_empty = res_empty.json()
        self.assertEqual(data_empty["total_count"], 0)
        self.assertEqual(data_empty["avg_overall"], 0.0)

        # 3. محاولة كتابة مراجعة قبل الشراء (يجب أن يرفض 403)
        rev_data = {
            "reviewer_title": "مدرس أول جيولوجيا",
            "content_quality_rating": 5,
            "print_formatting_rating": 4,
            "stamp_appearance_rating": 5,
            "comment": "مذكرة ممتازة وتنسيق رائع"
        }
        res_fail = self.client.post(f"/api/materials/{material.id}/reviews", json=rev_data, headers=headers)
        self.assertEqual(res_fail.status_code, 403)

        # 4. محاكاة شراء المادة وإكمالها
        purchase = Purchase(
            buyer_id=reviewer.id,
            material_id=material.id,
            buyer_name_stamp="الأستاذ مصطفى",
            buyer_phone_stamp="01099998888",
            amount_paid=15.0,
            status=PurchaseStatus.COMPLETED
        )
        self.db.add(purchase)
        self.db.commit()

        # 5. كتابة المراجعة بعد إتمام الشراء (يجب أن تنجح 200)
        res_rev = self.client.post(f"/api/materials/{material.id}/reviews", json=rev_data, headers=headers)
        self.assertEqual(res_rev.status_code, 200)
        rev_out = res_rev.json()
        self.assertEqual(rev_out["reviewer_name"], "الأستاذ مصطفى كامل")
        self.assertEqual(rev_out["overall_rating"], round((5 + 4 + 5) / 3.0, 2))

        # 6. جلب التقييمات مجدداً والتحقق من حساب المتوسطات
        res_list = self.client.get(f"/api/materials/{material.id}/reviews")
        self.assertEqual(res_list.status_code, 200)
        data_list = res_list.json()
        self.assertEqual(data_list["total_count"], 1)
        self.assertEqual(data_list["avg_content_quality"], 5.0)
        self.assertEqual(data_list["avg_print_formatting"], 4.0)
        self.assertEqual(data_list["avg_stamp_appearance"], 5.0)
        self.assertEqual(data_list["avg_overall"], round((5 + 4 + 5) / 3.0, 1))
        self.assertEqual(len(data_list["reviews"]), 1)
        self.assertEqual(data_list["reviews"][0]["comment"], "مذكرة ممتازة وتنسيق رائع")


if __name__ == "__main__":
    unittest.main()


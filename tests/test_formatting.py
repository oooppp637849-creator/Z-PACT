import sys
import os

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.formatting import format_instructor_name, format_contact_phone


def test_instructor_name_formatting():
    # 1. Standard teacher variations -> standardized to "أ / "
    assert format_instructor_name("أ/ محمد") == "أ / محمد"
    assert format_instructor_name("أ. محمد") == "أ / محمد"
    assert format_instructor_name("أ / محمد") == "أ / محمد"
    assert format_instructor_name("أ \\ محمد") == "أ / محمد"
    assert format_instructor_name("أ\\ محمد") == "أ / محمد"
    assert format_instructor_name("أ   / محمد") == "أ / محمد"
    assert format_instructor_name("أستاذ محمد") == "أ / محمد"
    assert format_instructor_name("الاستاذ محمد") == "أ / محمد"
    
    # 2. Double or repeated prefixes -> stripped to single "أ / "
    assert format_instructor_name("أ / أ / محمد") == "أ / محمد"
    assert format_instructor_name("أستاذ أ / علي") == "أ / علي"
    
    # 3. No prefix -> auto-prepends "أ / "
    assert format_instructor_name("محمود") == "أ / محمود"
    assert format_instructor_name("خالد عبد الله") == "أ / خالد عبد الله"
    
    # 4. Professional titles -> PRESERVED exactly, NO "أ / " added
    assert format_instructor_name("م / علي") == "م / علي"
    assert format_instructor_name("مهندس أحمد") == "مهندس أحمد"
    assert format_instructor_name("المهندس خالد") == "المهندس خالد"
    assert format_instructor_name("د / محمد") == "د / محمد"
    assert format_instructor_name("دكتور سارة") == "دكتور سارة"
    assert format_instructor_name("د. عمرو") == "د. عمرو"
    assert format_instructor_name("أ.د إبراهيم") == "أ.د إبراهيم"
    assert format_instructor_name("بشمهندس عمر") == "بشمهندس عمر"
    
    # 5. Redundant teacher prefix before professional title -> cleaned
    assert format_instructor_name("أ / دكتور محمد") == "دكتور محمد"
    
    print("✅ All instructor name formatting tests passed successfully!")


def test_contact_phone_formatting():
    # 1. Standard phone variations -> standardized to "ت / "
    assert format_contact_phone("ت. 01012345678") == "ت / 01012345678"
    assert format_contact_phone("ت / 01012345678") == "ت / 01012345678"
    assert format_contact_phone("ت\\ 01012345678") == "ت / 01012345678"
    assert format_contact_phone("ت \\ 01012345678") == "ت / 01012345678"
    assert format_contact_phone("ت . 01012345678") == "ت / 01012345678"
    assert format_contact_phone("تليفون: 01122334455") == "ت / 01122334455"
    assert format_contact_phone("هاتف / 0123456789") == "ت / 0123456789"
    
    # 2. Double or repeated phone prefixes -> stripped to single "ت / "
    assert format_contact_phone("ت / ت / 01012345678") == "ت / 01012345678"
    assert format_contact_phone("تليفون: ت / 01122334455") == "ت / 01122334455"
    
    # 3. No prefix -> auto-prepends "ت / "
    assert format_contact_phone("01099887766") == "ت / 01099887766"
    
    print("✅ All contact phone formatting tests passed successfully!")


def test_clean_phone_number_formatting():
    from app.formatting import clean_phone_number
    # 1. Standard variations -> clean phone number with NO prefix
    assert clean_phone_number("01012345678") == "01012345678"
    assert clean_phone_number("ت. 01012345678") == "01012345678"
    assert clean_phone_number("ت / 01012345678") == "01012345678"
    assert clean_phone_number("ت\\ 01012345678") == "01012345678"
    assert clean_phone_number("ت \\ 01012345678") == "01012345678"
    assert clean_phone_number("تليفون: 01012345678") == "01012345678"
    assert clean_phone_number("هاتف: 01012345678") == "01012345678"
    assert clean_phone_number("موبايل / 01012345678") == "01012345678"
    
    # 2. Repeated prefixes
    assert clean_phone_number("ت / ت / 01012345678") == "01012345678"
    
    print("✅ All clean phone number tests passed successfully!")


if __name__ == "__main__":
    test_instructor_name_formatting()
    test_contact_phone_formatting()
    test_clean_phone_number_formatting()

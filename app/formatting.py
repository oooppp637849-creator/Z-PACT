import re

# Separator pattern: matches one or more spaces, dots, slashes, backslashes, colons, or hyphens
SEP = r'[\.\/\\:\-\s]+'

# Regex for detecting professional titles that should NOT receive the "أ /" prefix
PROFESSIONAL_TITLES_REGEX = re.compile(
    r'^(?:أ\.?\s*د|دكتور|الدكتور|د|مهندس|المهندس|بشمهندس|م|بروفيسور|مستشار|المستشار|لواء|اللواء|dr|eng|prof|mr|mrs|ms)' + SEP,
    re.UNICODE | re.IGNORECASE
)

# Regex for detecting standard teacher/instructor prefixes
TEACHER_PREFIX_REGEX = re.compile(
    r'^(?:أستاذ|الأستاذ|استاذ|الاستاذ|أ)' + SEP,
    re.UNICODE | re.IGNORECASE
)

# Regex for detecting phone/contact prefixes
PHONE_PREFIX_REGEX = re.compile(
    r'^(?:تليفون|هاتف|موبايل|جوال|ت)' + SEP,
    re.UNICODE | re.IGNORECASE
)


def format_instructor_name(name: str) -> str:
    """
    Intelligently formats an instructor's name:
    1. Strips messy or repeated teacher prefixes ("أ/", "أ.", "أ /", "أستاذ").
    2. Preserves professional titles ("م /", "مهندس", "د /", "دكتور") without adding "أ /".
    3. Standardizes regular names by prepending "أ / ".
    """
    if not name or not isinstance(name, str):
        return ""
        
    cleaned = name.strip()
    
    # Check if input already starts with a professional title
    if PROFESSIONAL_TITLES_REGEX.match(cleaned):
        return cleaned
        
    # Strip all occurrences of teacher prefixes (handles double prefixes like "أ / أ /")
    while True:
        m = TEACHER_PREFIX_REGEX.match(cleaned)
        if m:
            cleaned = cleaned[m.end():].strip()
        else:
            break
            
    # After stripping teacher prefixes, check again if what remains is a professional title
    # (e.g., if user input was "أ / دكتور محمد")
    if PROFESSIONAL_TITLES_REGEX.match(cleaned):
        return cleaned
        
    return f"أ / {cleaned}" if cleaned else ""


def clean_phone_number(phone: str) -> str:
    """
    Strips any contact/phone prefixes ("ت.", "ت /", "ت\\", "تليفون:", "هاتف:", etc.)
    and returns just the pure phone number string without any prefix.
    Used especially for the cover page (Page 1) to display the phone number only.
    """
    if not phone or not isinstance(phone, str):
        return ""
        
    cleaned = phone.strip()
    
    # Strip all occurrences of phone prefixes (handles double prefixes like "ت / ت /")
    while True:
        m = PHONE_PREFIX_REGEX.match(cleaned)
        if m:
            cleaned = cleaned[m.end():].strip()
        else:
            break
            
    # Clean any residual slashes, colons, hyphens at the start
    cleaned = cleaned.lstrip('/\\:.- ')
    return cleaned


def format_contact_phone(phone: str) -> str:
    """
    Intelligently formats a phone/contact string:
    1. Strips any messy or repeated contact prefixes ("ت.", "ت /", "ت\\", "تليفون:").
    2. Standardizes by prepending "ت / ".
    """
    cleaned = clean_phone_number(phone)
    return f"ت / {cleaned}" if cleaned else ""

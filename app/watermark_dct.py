import cv2
import numpy as np
from PIL import Image
import os

SYNC_PATTERN = [1, 0, 1, 0, 1, 0, 1, 0]

def _int_to_bits(val: int, num_bits: int) -> list[int]:
    """تحويل رقم صحيح لمصفوفة من البتات"""
    return [(val >> i) & 1 for i in range(num_bits - 1, -1, -1)]

def _bits_to_int(bits: list[int]) -> int:
    """تحويل مصفوفة بتات لرقم صحيح"""
    val = 0
    for b in bits:
        val = (val << 1) | b
    return val

def make_bitstream(purchase_id: int) -> list[int]:
    """
    بناء مصفوفة البتات (48 بت):
      - 8 بت: sync pattern (10101010)
      - 32 بت: purchase_id
      - 8 بت: XOR checksum
    """
    # 32-bit purchase_id
    id_bits = _int_to_bits(purchase_id, 32)
    
    # Calculate checksum
    bytes_list = [
        (purchase_id >> 24) & 0xFF,
        (purchase_id >> 16) & 0xFF,
        (purchase_id >> 8) & 0xFF,
        purchase_id & 0xFF
    ]
    checksum = bytes_list[0] ^ bytes_list[1] ^ bytes_list[2] ^ bytes_list[3]
    checksum_bits = _int_to_bits(checksum, 8)
    
    return SYNC_PATTERN + id_bits + checksum_bits

def embed_dct_watermark(image_path: str, purchase_id: int, delta: float = 12.0) -> None:
    """
    تضمين العلامة المائية غير المرئية في نطاق التردد (DCT) للملف المولد
    """
    if not os.path.exists(image_path):
        return
        
    # قراءة الصورة عبر OpenCV
    img = cv2.imread(image_path)
    if img is None:
        return
        
    # تحويل الصورة إلى YCrCb للعمل على قناة الإضاءة (Luminance - Y) لعدم تدمير الألوان
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    y_channel = ycrcb[:, :, 0].copy()
    
    h, w = y_channel.shape
    blocks_h = h // 8
    blocks_w = w // 8
    
    # إنشاء البتات المراد تضمينها
    bitstream = make_bitstream(purchase_id)
    stream_len = len(bitstream)
    
    block_idx = 0
    # المرور على كتل 8x8 وتطبيق الـ DCT
    for r in range(blocks_h):
        for c in range(blocks_w):
            # استخراج الكتلة
            block = y_channel[r*8:(r+1)*8, c*8:(c+1)*8].astype(np.float32)
            
            # تطبيق 2D DCT
            dct_block = cv2.dct(block)
            
            # البت المراد تضمينه في هذه الكتلة (تكرار البتات لزيادة الأمان والصمود أمام القص)
            bit = bitstream[block_idx % stream_len]
            block_idx += 1
            
            # نختار معاملات التردد المتوسط (3, 4) و (4, 3) لضمان عدم تأثرها بالضغط
            # C1 = dct_block[3, 4], C2 = dct_block[4, 3]
            c1, c2 = dct_block[3, 4], dct_block[4, 3]
            
            # تعديل العلاقة بين المعاملين بناءً على قيمة البت
            if bit == 0:
                if c1 - c2 <= delta:
                    avg = (c1 + c2) / 2.0
                    dct_block[3, 4] = avg + delta / 2.0
                    dct_block[4, 3] = avg - delta / 2.0
            else: # bit == 1
                if c2 - c1 <= delta:
                    avg = (c1 + c2) / 2.0
                    dct_block[3, 4] = avg - delta / 2.0
                    dct_block[4, 3] = avg + delta / 2.0
            
            # تطبيق 2D Inverse DCT
            idct_block = cv2.idct(dct_block)
            
            # قص القيم بين 0 و 255 وحفظها في القناة
            y_channel[r*8:(r+1)*8, c*8:(c+1)*8] = np.clip(idct_block, 0, 255).astype(np.uint8)
            
    # دمج القنوات وحفظ الصورة
    ycrcb[:, :, 0] = y_channel
    final_img = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
    cv2.imwrite(image_path, final_img)

def extract_dct_watermark(image_path: str):
    """
    استرجاع الـ purchase_id من أي صورة (أو سكرين شوت) مختومة بترددات DCT
    """
    if not os.path.exists(image_path):
        return None
        
    img = cv2.imread(image_path)
    if img is None:
        return None
        
    # تحويل الصورة إلى YCrCb واستخراج قناة الـ Y
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    y_channel = ycrcb[:, :, 0]
    
    h, w = y_channel.shape
    blocks_h = h // 8
    blocks_w = w // 8
    
    stream_len = 48
    # votes[i][0] = عدد الأصوات للبت 0 في الموقع i
    # votes[i][1] = عدد الأصوات للبت 1 في الموقع i
    votes = np.zeros((stream_len, 2), dtype=np.int32)
    
    block_idx = 0
    for r in range(blocks_h):
        for c in range(blocks_w):
            block = y_channel[r*8:(r+1)*8, c*8:(c+1)*8].astype(np.float32)
            dct_block = cv2.dct(block)
            
            c1, c2 = dct_block[3, 4], dct_block[4, 3]
            bit = 0 if c1 > c2 else 1
            
            votes[block_idx % stream_len, bit] += 1
            block_idx += 1
            
    # حساب القيمة النهائية للبتات بالأغلبية
    extracted_bits = []
    for i in range(stream_len):
        if votes[i, 0] > votes[i, 1]:
            extracted_bits.append(0)
        else:
            extracted_bits.append(1)
            
    # البحث عن الـ Sync Pattern بالتجربة الدائرية (Cyclic Shift) لتعويض إزاحة القص
    for shift in range(stream_len):
        shifted_bits = extracted_bits[shift:] + extracted_bits[:shift]
        
        # التحقق من تطابق الـ Sync
        if shifted_bits[:8] == SYNC_PATTERN:
            # استخراج الـ purchase_id والـ checksum
            id_bits = shifted_bits[8:40]
            chk_bits = shifted_bits[40:48]
            
            purchase_id = _bits_to_int(id_bits)
            checksum = _bits_to_int(chk_bits)
            
            # التحقق من صحة الـ checksum
            bytes_list = [
                (purchase_id >> 24) & 0xFF,
                (purchase_id >> 16) & 0xFF,
                (purchase_id >> 8) & 0xFF,
                purchase_id & 0xFF
            ]
            expected_chk = bytes_list[0] ^ bytes_list[1] ^ bytes_list[2] ^ bytes_list[3]
            
            if checksum == expected_chk:
                return purchase_id
                
    return None

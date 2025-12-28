import os
import requests
import time
import random
from PIL import Image
from io import BytesIO

# ฟังก์ชันแยกคำหลัก (Keywords) ออกจากประโยค
def extract_keywords(prompt):
    # คำที่ไม่เอา (Stop words)
    ignore_words = ['a', 'an', 'the', 'of', 'in', 'on', 'at', 'with', 'to', 'for', 'is', 'are', 'background', 'style', 'view']
    
    # ลบเครื่องหมายวรรคตอนและแยกคำ
    clean_prompt = prompt.replace(',', '').replace('.', '')
    words = clean_prompt.split()
    
    # เลือกเฉพาะคำที่มีความหมาย (ไม่ใช่ stop words)
    keywords = [w for w in words if w.lower() not in ignore_words]
    
    # เอาแค่ 3 คำแรกก็พอ (เยอะไปเดี๋ยวหารูปยาก)
    return ",".join(keywords[:3])

def download_image(prompt, save_path, max_retries=3):
    # 1. เช็คไฟล์เดิม
    if os.path.exists(save_path):
        try:
            with Image.open(save_path) as img:
                img.verify()
            print(f"   [Image] File exists, skipping.")
            return
        except Exception:
            os.remove(save_path)

    # 2. สร้าง URL จาก Keywords
    keywords = extract_keywords(prompt)
    print(f"   [Image] Searching for: '{keywords}' ...")

    for attempt in range(1, max_retries + 1):
        # เพิ่ม random ท้าย url เพื่อให้ได้รูปไม่ซ้ำ
        seed = int(time.time()) + random.randint(1, 1000)
        
        # ใช้บริการ LoremFlickr (ค้นหารูปตามคีย์เวิร์ด)
        url = f"https://loremflickr.com/1080/1920/{keywords}/all?random={seed}"

        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # เช็คว่าเป็นรูปจริงไหม
                try:
                    image_data = BytesIO(response.content)
                    with Image.open(image_data) as img:
                        img.verify()
                    
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                    print(f"   ✅ [Image] Saved matching photo!")
                    return 
                except Exception:
                    pass # ถ้าไม่ใช่รูปให้วนลูปใหม่
            
        except Exception as e:
            print(f"   ⚠️ [Network] {e}")
        
        time.sleep(2)

    # 3. ถ้าหาไม่เจอจริงๆ สร้างภาพดำ
    print(f"   ❌ [Error] Not found. Creating Black Screen.")
    img = Image.new('RGB', (1080, 1920), color=(0, 0, 0))
    img.save(save_path)
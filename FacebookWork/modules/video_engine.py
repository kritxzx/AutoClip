from moviepy import ImageClip, AudioFileClip, CompositeVideoClip
import numpy as np
from PIL import Image  # <--- เพิ่มบรรทัดนี้

def process_scene(image_path, audio_path):
    print(f"   [Video] Processing scene...")

    # 1. โหลดเสียง
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration + 0.1

    # 2. โหลดภาพ (แก้ส่วนนี้: ใช้ PIL อ่านแล้วแปลงเป็น Numpy Array)
    # วิธีนี้จะแก้ปัญหา imageio หา backend ไม่เจอ
    pil_image = Image.open(image_path).convert('RGB')
    img_array = np.array(pil_image)
    
    img_clip = ImageClip(img_array).with_duration(duration)

    # 3. Ken Burns Effect (สูตรแก้ลายน้ำ)
    # เดิม: lambda t: 1 + 0.04 * t  (เริ่มที่ 100%)
    # ใหม่: lambda t: 1.15 + 0.05 * t (เริ่มที่ 115% ลายน้ำตกขอบแน่นอน)
    zoom_clip = img_clip.resized(lambda t: 1.15 + 0.05 * t) 
    
    # จัดตำแหน่งให้อยู่ตรงกลาง (Center Crop)
    zoom_clip = zoom_clip.with_position(('center', 'center'))

    # 4. รวมร่าง (บังคับไซส์ 1080x1920)
    final_clip = CompositeVideoClip([zoom_clip], size=(1080, 1920))
    final_clip = final_clip.with_audio(audio_clip)

    return final_clip
import json
import os
import asyncio
# ใช้ moviepy.editor เพื่อความชัวร์ในการเรียกฟังก์ชันตัดต่อ
from moviepy.editor import concatenate_videoclips, VideoFileClip

# Import โมดูลจากโฟลเดอร์ modules
from modules import image_gen, audio_gen, video_engine

# --- ตั้งค่าชื่อโปรเจกต์ (ต้องตรงกับชื่อไฟล์ใน scripts/) ---
PROJECT_NAME = "story_01"

print("🚀 System Initializing... (โปรแกรมเริ่มทำงานแล้ว)")

async def main():
    # 0. ตรวจสอบและสร้างโฟลเดอร์ที่จำเป็น
    print("📁 Checking directories...")
    os.makedirs("assets/images", exist_ok=True)
    os.makedirs("assets/audio", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # 1. โหลดไฟล์บทจาก JSON
    script_path = f"scripts/{PROJECT_NAME}.json"
    if not os.path.exists(script_path):
        print(f"❌ Error: Script file not found at {script_path}")
        print("   -> กรุณาตรวจสอบว่ามีไฟล์ .json ในโฟลเดอร์ scripts หรือไม่")
        return

    try:
        with open(script_path, "r", encoding="utf-8") as f:
            script_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        return

    all_clips = []
    print(f"=== Starting Project: {PROJECT_NAME} ===")

    # 2. วนลูปทำทีละซีน
    for scene in script_data:
        scene_id = scene.get('id', 'unknown')
        print(f"\n🎬 Processing Scene {scene_id}...")
        
        # ตั้งชื่อไฟล์
        img_path = f"assets/images/{PROJECT_NAME}_scene_{scene_id}.jpg"
        audio_path = f"assets/audio/{PROJECT_NAME}_scene_{scene_id}.mp3"

        # 2.1 สร้างรูปภาพ (Image Generation)
        # ฟังก์ชันนี้เป็น Sync (ไม่ต้อง await)
        try:
            image_gen.download_image(scene['image_prompt'], img_path)
        except Exception as e:
            print(f"   ⚠️ Image Gen Error: {e}")

        # 2.2 สร้างเสียง (Audio Generation)
        # ฟังก์ชันนี้มักเป็น Async (ต้อง await)
        try:
            if not os.path.exists(audio_path): # เช็คว่ามีเสียงอยู่แล้วไหมจะได้ไม่สร้างซ้ำ
                await audio_gen.create_voice(scene['text'], audio_path)
            else:
                print("   [Audio] File exists, skipping generation.")
        except Exception as e:
            print(f"   ⚠️ Audio Gen Error: {e}")

        # 2.3 รวมภาพและเสียงเป็นคลิปวิดีโอสั้นๆ
        if os.path.exists(img_path) and os.path.exists(audio_path):
            try:
                clip = video_engine.process_scene(img_path, audio_path)
                if clip:
                    all_clips.append(clip)
                    print(f"   ✅ Scene {scene_id} ready.")
            except Exception as e:
                print(f"   ⚠️ Video Processing Error: {e}")
        else:
            print("   ❌ Error: Missing assets for this scene (Skipping).")

    # 3. รวมไฟล์และ Export เป็นไฟล์เดียว
    if all_clips:
        print("\n🎞️  Rendering Final Video... (Please wait)")
        try:
            final_video = concatenate_videoclips(all_clips, method="compose")
            
            output_path = f"output/{PROJECT_NAME}_final.mp4"
            
            # fps=24 (หนัง), threads=4 (เร่งความเร็ว CPU)
            final_video.write_videofile(
                output_path, 
                fps=24, 
                codec='libx264', 
                audio_codec='aac',
                preset='ultrafast',  # ใช้ ultrafast ตอนเทส (ถ้าเอาจริงเปลี่ยนเป็น medium)
                threads=4
            )
            print(f"\n🎉 Done! Video saved at: {output_path}")
        except Exception as e:
            print(f"❌ Render Error: {e}")
    else:
        print("❌ No clips to render. Check errors above.")

# --- ส่วนสำคัญที่สุด: สั่งรันโปรแกรม ---
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Program stopped by user.")
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")
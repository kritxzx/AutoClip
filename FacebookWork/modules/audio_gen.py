import os
import edge_tts

# เสียงพากย์ภาษาไทยที่แนะนำ:
# th-TH-PremwadeeNeural (หญิง)
# th-TH-NiwatNeural (ชาย)
VOICE = "th-TH-NiwatNeural"
SPEED = "+0%"
async def create_voice(text, save_path):
    if os.path.exists(save_path):
        print(f"   [Audio] File exists, skipping: {save_path}")
        return

    print(f"   [Audio] Generating voice...")
    try:
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(save_path)
        print(f"   [Audio] Saved to {save_path}")
    except Exception as e:
        print(f"   [Error] Audio generation failed: {e}")
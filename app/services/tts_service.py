import edge_tts

async def generate_tts(text, voice, output_file, rate="+0%", volume="+0%", pitch="-3Hz"):
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate, volume=volume, pitch=pitch)
    submaker = edge_tts.SubMaker()
    
    with open(output_file, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                submaker.feed(chunk)
                
    srt_file = output_file.replace(".mp3", ".srt")
    with open(srt_file, "w", encoding="utf-8") as f:
        f.write(submaker.get_srt())
        
    return srt_file

def calculate_rate(text: str, target_duration: float) -> str:
    word_count = len(text.split())
    natural_duration = word_count / 2.5  # 150 từ/phút = 2.5 từ/giây
    
    ratio = natural_duration / target_duration
    percent = round((ratio - 1) * 100)
    
    # Giới hạn trong khoảng edge-tts hỗ trợ
    percent = max(-50, min(50, percent))
    
    if percent >= 0:
        return f"+{percent}%"
    return f"{percent}%"


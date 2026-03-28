import edge_tts

async def generate_tts(text, voice, output_file, rate="+0%", volume="+0%", pitch="-3Hz"):
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate, volume=volume, pitch=pitch)
    await communicate.save(output_file)
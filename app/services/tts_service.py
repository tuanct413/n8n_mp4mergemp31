import edge_tts

async def generate_tts(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice=voice)
    await communicate.save(output_file)
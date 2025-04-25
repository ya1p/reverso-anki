import os
import json
import subprocess
from pydub import AudioSegment
import pyttsx3


def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config):
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def get_voices_for_language(language_code):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    matching_voices = []

    for voice in voices:
        if any(language_code in lang for lang in voice.languages):
            matching_voices.append((voice.name, voice.id))

    return matching_voices

def choose_voice(language_code):
    voices = get_voices_for_language(language_code)
    if not voices:
        print(f"❌ There are no voices for the code: '{language_code}'")
        return None

    print(f"🔊 Available voices for language '{language_code}':")
    for idx, (name, voice_id) in enumerate(voices):
        print(f"{idx + 1}. {name}")

    while True:
        choice = input("Enter your preferred voice number: ")
        if choice.isdigit() and 1 <= int(choice) <= len(voices):
            return voices[int(choice) - 1][0]
        print("❌ Wrong choice. Try again.")

def save_speech(sentence, filename, voice, rate=180, audio_format="mp3"):
    output_path = f"voices/{filename}.{audio_format}"

    if os.path.exists(output_path):
        print(f"⏩ Skipped: {output_path} already exists")
        return

    temp_aiff = "temp_output.aiff"

    subprocess.run([
        "say",
        "-v", voice,
        "-r", str(rate),
        sentence,
        "-o", temp_aiff
    ])

    audio = AudioSegment.from_file(temp_aiff, format="aiff")
    audio.export(output_path, format=audio_format)
    os.remove(temp_aiff)
    print(f"✅ Saved: {output_path}")

def make_voices(sentences, word):
    os.makedirs("voices", exist_ok=True)
    config = load_config()

    voice = config.get("voice_name")
    rate = config.get("rate", 180)
    audio_format = config.get("audio_format", "mp3")
    language_code = config.get("language_code", "en")

    if not voice:
        print("🗣️  No voice selected yet.")
        voice = choose_voice(language_code)
        if not voice:
            print("❌ Voice selection failed. Skipping voice generation.")
            return
        config["voice_name"] = voice
        save_config(config)
        print(f"💾 Voice '{voice}' saved to config.")

    for i, sentence in enumerate(sentences):
        save_speech(sentence, f"{word}{i+1}", voice, rate, audio_format)
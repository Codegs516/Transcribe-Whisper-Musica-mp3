import whisper
import os
from datetime import timedelta
from langdetect import detect
from deep_translator import GoogleTranslator

def format_timestamp(seconds):
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{timedelta(seconds=int(seconds))},{milliseconds:03d}"

def split_text(text, max_words=5):
    words = text.split()
    lines = []
    for i in range(0, len(words), max_words):
        lines.append(" ".join(words[i:i + max_words]))
    return "\n".join(lines) if lines else "🎵"

def transcribe_audio(audio_path, model):
    print("⏳ Transcribiendo el audio... ¡Paciencia!")
    result = model.transcribe(audio_path)
    return result

def save_srt(transcription, output_path):
    with open(output_path, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(transcription["segments"], start=1):
            start_time = format_timestamp(segment["start"])
            end_time = format_timestamp(segment["end"])
            text = split_text(segment["text"].upper())
            srt_file.write(f"{i}\n{start_time} --> {end_time}\n{text}\n\n")
    print(f"✅ Archivo SRT guardado: {output_path}")

def main():
    audio_path = input("🎵 ¡Hey! ¿Dónde está tu archivo MP3? Dame la ruta completa: ")
    if not os.path.exists(audio_path):
        print("❌ Archivo no encontrado. Verifica la ruta e inténtalo de nuevo.")
        return
    
    model = whisper.load_model("medium")  # Modelo más rápido y preciso
    result = transcribe_audio(audio_path, model)
    
    srt_original = "transcripcion_original.srt"
    save_srt(result, srt_original)
    
    detected_lang = detect(result['text'])
    print(f"🌍 Detecté que el idioma principal de la canción es: {detected_lang.upper()}")
    
    if detected_lang != "es":
        translate_option = input("💬 ¿Quieres una transcripción en ESPAÑOL con el sentimiento original? (sí/no): ")
        if translate_option.lower() in ["si", "sí", "yes"]:
            translated_text = GoogleTranslator(source=detected_lang, target="es").translate(result["text"])
            
            translated_segments = []
            for segment in result['segments']:
                translated_segments.append({
                    "start": segment['start'],
                    "end": segment['end'],
                    "text": split_text(GoogleTranslator(source=detected_lang, target="es").translate(segment['text']).upper())
                })
            
            srt_translated = "transcripcion_espanol.srt"
            save_srt({"segments": translated_segments}, srt_translated)

if __name__ == "__main__":
    main()

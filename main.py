import os
import speech_recognition as sr
from moviepy import VideoFileClip
from pydub import AudioSegment
from pydub.utils import which
from tkinter import Tk, filedialog
from tqdm import tqdm  

AudioSegment.converter = which("ffmpeg")

def dividir_audio(audio_path, chunk_length_ms=60000):
    audio = AudioSegment.from_wav(audio_path)
    chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i + chunk_length_ms]
        chunk_path = f"{audio_path}_chunk_{i // chunk_length_ms}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    return chunks

def transcribir_audio_por_chunks(audio_chunks, recognizer):
    texto_total = ""
    for i, chunk_path in enumerate(tqdm(audio_chunks, desc="Transcribiendo audio", unit="fragmento")):
        with sr.AudioFile(chunk_path) as source:
            audio = recognizer.record(source)
            try:
                texto = recognizer.recognize_google(audio, language="es-MX")
                texto_total += f"[Fragmento {i + 1}]\n{texto}\n\n"
            except sr.UnknownValueError:
                texto_total += f"[Fragmento {i + 1}] No se entendió el audio.\n\n"
            except sr.RequestError as e:
                texto_total += f"[Fragmento {i + 1}] Error de reconocimiento: {e}\n\n"
        os.remove(chunk_path)  
    return texto_total

def main():
    Tk().withdraw()
    video_path = filedialog.askopenfilename(
        title="Selecciona un video",
        filetypes=[("Archivos de video", "*.mp4 *.mov *.avi *.mkv")]
    )

    if video_path:
        print(f"Video seleccionado: {video_path}")

        audio_path = video_path.rsplit(".", 1)[0] + ".wav"
        videoclip = VideoFileClip(video_path)
        videoclip.audio.write_audiofile(audio_path)

        audio_chunks = dividir_audio(audio_path)

        recognizer = sr.Recognizer()
        texto_final = transcribir_audio_por_chunks(audio_chunks, recognizer)

        output_dir = r"C:\Documentos\Transcript\Text"
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.basename(video_path).rsplit(".", 1)[0]
        output_file = os.path.join(output_dir, f"{base_name}.txt")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(texto_final)

        print(f"✅ Transcripción guardada en: {output_file}")
        os.remove(audio_path)  
    else:
        print("❌ No se seleccionó ningún archivo.")

if __name__ == "__main__":
    main()

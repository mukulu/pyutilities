#!/usr/bin/env python3

import os
import warnings
from pydub import AudioSegment
import torch
import torchaudio
import tempfile
from transformers import pipeline
from moviepy.video.io.VideoFileClip import VideoFileClip

# Suppress TensorFlow / HuggingFace non-critical warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
warnings.filterwarnings("ignore")

def convert_mp3_to_wav(mp3_path, wav_path):
    """Convert MP3 file to WAV format."""
    audio = AudioSegment.from_mp3(mp3_path)
    audio.export(wav_path, format="wav")
    return wav_path

def transcribe_audio(wav_file_path):
    """Transcribe WAV audio using Whisper (with long-form support)."""
    device = 0 if torch.cuda.is_available() else -1
    asr = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-base",
        device=device,
        return_timestamps=True  # Fix for >30s audio
    )
    output = asr(wav_file_path)
    return output["text"]

def process_media_file(file_path, total_files, current_index):
    dir_name = os.path.dirname(file_path)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    txt_path = os.path.join(dir_name, f"{base_name}.txt")

    if os.path.exists(txt_path):
        print(f"[{current_index}/{total_files}] ⏭ Already exists: {txt_path}")
        return

    print(f"[{current_index}/{total_files}] 🎙 Transcribing: {file_path}")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        try:
            if file_path.lower().endswith(".mp3"):
                convert_mp3_to_wav(file_path, tmp_wav.name)
            elif file_path.lower().endswith(".mp4"):
                extract_audio_from_mp4(file_path, tmp_wav.name)
            else:
                print(f"    ⚠ Unsupported file type: {file_path}")
                return

            transcript = transcribe_audio(tmp_wav.name)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(transcript)
            print(f"    ✅ Transcript saved to: {txt_path}")
        except Exception as e:
            print(f"    ❌ Error processing {file_path}: {e}")
        finally:
            os.remove(tmp_wav.name)

def find_all_media_files(root_dir):
    """Recursively find all .mp3 and .mp4 files."""
    media_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.lower().endswith((".mp3", ".mp4")):
                media_files.append(os.path.join(dirpath, file))
    return media_files

def extract_audio_from_mp4(mp4_path, wav_path):
    """Extract audio from MP4 and save as WAV."""
    video = VideoFileClip(mp4_path)
    audio = video.audio
    audio.write_audiofile(wav_path, codec='pcm_s16le')
    return wav_path

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    media_files = find_all_media_files(root_dir)

    if not media_files:
        print("❗ No MP3 or MP4 files found.")
        return

    print(f"\n🔍 Found {len(media_files)} media files to transcribe:\n")
    for i, file in enumerate(media_files, 1):
        print(f"  {i}. {os.path.relpath(file, root_dir)}")

    print("\n🚀 Starting transcription process...\n")
    for i, file_path in enumerate(media_files, 1):
        process_media_file(file_path, len(media_files), i)
        percent = (i / len(media_files)) * 100
        print(f"📊 Progress: {percent:.2f}% complete\n")

    print("✅ All transcriptions completed.\n")

if __name__ == "__main__":
    main()

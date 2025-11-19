import streamlit as st
from audiorecorder import audiorecorder
import datetime
from pydub import AudioSegment
from io import BytesIO

st.title("🎙️ Audio Recorder - Save as WAV")

st.write("Click **start recording**, then **stop**, then the file will be saved automatically.")

# Audio recorder component
audio = audiorecorder("Start Recording 🎤", "Stop Recording 🛑")

if len(audio) > 0:
    # Convert AudioSegment to bytes
    audio_bytes = BytesIO()
    audio.export(audio_bytes, format="wav")
    audio_bytes.seek(0)  # Rewind the BytesIO stream to the beginning

    # Display the recorded audio as a preview (WAV format)
    st.audio(audio_bytes, format="audio/wav")

    # Save the audio directly as a WAV file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    wav_file = f"recording_{timestamp}.wav"
    
    with open(wav_file, "wb") as f:
        f.write(audio_bytes.read())

    st.success(f"🎉 Recording saved as `{wav_file}`")

    # Provide download button for the WAV file
    st.download_button("⬇️ Download WAV", data=open(wav_file, "rb"), file_name=wav_file)

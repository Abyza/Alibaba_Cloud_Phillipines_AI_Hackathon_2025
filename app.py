import streamlit as st
from audiorecorder import audiorecorder
import datetime
import json
import os
from pydub import AudioSegment
from io import BytesIO
from utils import *  # Import everything from the utils.py file

# Sidebar for healthcare provider details
st.sidebar.title("Healthcare Provider Information")

provider_name = st.sidebar.text_input("Healthcare Provider Name")
address = st.sidebar.text_area("Address")
contact_number = st.sidebar.text_input("Contact Number")
doctor_name = st.sidebar.text_input("Doctor Name")
doctor_title = st.sidebar.text_input("Doctor Title")
logo_file = st.sidebar.file_uploader("Upload Provider Logo", type=["jpg", "jpeg", "png"])

# Create a directory to save images if it doesn't exist
if not os.path.exists("provider_logos"):
    os.makedirs("provider_logos")

# Static file names for storing provider information and logo
provider_info_filename = "provider_info.json"
logo_filename = "provider_logos/logo.jpg"  # Static filename for the logo (overwrite)

# Save button functionality
if st.sidebar.button("Save Information"):
    # Create a dictionary with the entered information
    provider_info = {
        "provider_name": provider_name,
        "address": address,
        "contact_number": contact_number,
        "doctor_name": doctor_name,
        "doctor_title": doctor_title,
    }
    
    # Save the logo with a static name if uploaded
    if logo_file is not None:
        with open(logo_filename, "wb") as f:
            f.write(logo_file.getbuffer())
        provider_info["logo_file"] = logo_filename  # Save the path of the logo file

    # Save the information to the static JSON file on the server
    with open(provider_info_filename, "w") as f:
        json.dump(provider_info, f, indent=4)

    st.sidebar.success(f"Information saved successfully as `{provider_info_filename}`!")

    # Optionally, provide a way to download the saved file
    with open(provider_info_filename, "rb") as f:
        st.sidebar.download_button("⬇️ Download Saved Info", data=f, file_name=provider_info_filename)

# Display the entered details in the sidebar (Optional)
st.sidebar.write("### Entered Details")
st.sidebar.write(f"**Healthcare Provider Name**: {provider_name}")
st.sidebar.write(f"**Address**: {address}")
st.sidebar.write(f"**Contact Number**: {contact_number}")
st.sidebar.write(f"**Doctor Name**: {doctor_name}")
st.sidebar.write(f"**Doctor Title**: {doctor_title}")

if logo_file is not None:
    st.sidebar.image(logo_file, caption="Logo Preview", use_container_width=True)

# Main title of the app
st.title("🎙️ InstantRx: Just Say It!")
st.write("Click **start recording**, then **stop**, and the prescription will be generated and downloaded automatically.")

# Audio recorder component
audio = audiorecorder("Start Recording 🎤", "Stop Recording 🛑")

# When recording is done, process the audio and generate PDF automatically
if len(audio) > 0:
    # Convert AudioSegment to bytes
    audio_bytes = BytesIO()
    audio.export(audio_bytes, format="wav")
    audio_bytes.seek(0)  # Rewind the BytesIO stream to the beginning

    # Display the recorded audio as a preview (WAV format)
    st.audio(audio_bytes, format="audio/wav")

    # Save the audio directly as a WAV file
   
    wav_file = f"recording.wav"
    
    with open(wav_file, "wb") as f:
        f.write(audio_bytes.read())

    st.success(f"🎉 Recording saved as `{wav_file}`")

    # Transcribe the audio and generate the prescription
    text_extracted = transcribe_audio(wav_file)
    generate_prescription_from_dictation(text_extracted)

    # Pretty JSON (not editable in the UI anymore)
    pretty_json = json.dumps(load_prescriptions(), indent=4)

    # Generate the PDF
    pdf_file = "prescription.pdf"
    generate_prescription_pdf()  # This will create 'prescription.pdf' on the server

    # Provide the option to automatically download the generated PDF file
    with open(pdf_file, "rb") as f:
        st.download_button("⬇️ Download Prescription PDF", data=f, file_name=pdf_file)


from openai import OpenAI

def transcribe_audio(audio_file_name: str):
    """Take an audio file name and return the transcript."""
    client = OpenAI()
    
    # Open the audio file
    with open(audio_file_name, "rb") as audio_file:
        # Create transcription request
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",  # Whisper-like STT model
            file=audio_file
        )
    
    return transcript.text


from langchain_qwq import ChatQwen
import json

def generate_prescription_from_dictation(text: str, file_name="prescription_output.json"):
    """Generate an e-prescription based on the doctor's dictation and save the response to a JSON file. If an error occurs, return a failure JSON."""
    llm = ChatQwen(
        model="qwen3-max",
        max_tokens=3_000,
        timeout=None,
        max_retries=2,
    )
    
    # Define strict instructions to output prescription details in JSON format
    messages = [
        (
            "system", 
            "You are an AI assistant that generates e-prescriptions based on the doctor's dictation. "
            "When the doctor dictates a prescription, extract all medications mentioned, along with their name, dosage, frequency, "
            "and any additional instructions or notes. Do not include any patient identifying information such as name. "
            "Output the prescription details as a list of JSON objects, each containing the following keys: "
            "'medication', 'dosage', 'frequency', and 'notes'. Ensure the output is in JSON format, with each medication as a separate object."
        ),
        ("human", text),  # This is the doctor's dictation input
    ]
    
    try:
        # Get the AI response
        ai_msg = llm.invoke(messages)
        
        # Parse the response to ensure it is valid JSON
        prescription_data = json.loads(ai_msg.content)

        # Check if the response is empty or invalid
        if not prescription_data:
            raise ValueError("Empty or invalid response received from AI.")
        
    except Exception as e:
        # On error, create a failure JSON object
        prescription_data = [
            {
                "medication": "fail",
                "dosage": "fail",
                "frequency": "fail",
                "notes": "fail"
            }
        ]
    
    # Write the prescription data (or failure) to a JSON file
    with open(file_name, "w") as json_file:
        json.dump(prescription_data, json_file, indent=4)
    
    return f"Prescription data saved to {file_name}"


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm  # Import mm here

from reportlab.lib.utils import ImageReader
import json
import os
import datetime

def generate_prescription_pdf(json_file="provider_info.json", logo_path="provider_logos/logo.jpg", output_pdf="prescription.pdf"):
    """
    Generates a PDF prescription using provider information from JSON and a logo image.
    Strictly uses only the data in the JSON file and logo image.
    """

    with open("prescription_output.json", "r") as f:
        prescription_data = json.load(f)
    
    # Load provider data from JSON
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"JSON file '{json_file}' not found.")
    
    with open(json_file, "r") as f:
        provider_info = json.load(f)

    # Get the current date
    current_date = datetime.datetime.now().strftime("%B %d, %Y")  # Example: November 20, 2025
    today_date_str = f"{current_date}"

    # Create a new PDF canvas
    pdf = canvas.Canvas(output_pdf, pagesize=A4)
    width, height = A4

    # Margins
    left_margin = 30 * mm
    top_margin = height - 30 * mm

    # --- Header Section ---
    if os.path.exists(logo_path):
        # Draw logo (fixed size)
        logo = ImageReader(logo_path)
        pdf.drawImage(logo, left_margin, top_margin - 30 * mm, width=40 * mm, height=40 * mm, mask='auto')
    else:
        print("⚠️ Logo file not found. Skipping logo section.")

    # Provider info text
    text_x = left_margin + 50 * mm
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(text_x, top_margin - 10 * mm, provider_info.get("provider_name", ""))
    
    pdf.setFont("Helvetica", 10)
    pdf.drawString(text_x, top_margin - 16 * mm, provider_info.get("address", ""))
    pdf.drawString(text_x, top_margin - 22 * mm, f"Contact: {provider_info.get('contact_number', '')}")
    pdf.drawString(text_x, top_margin - 28 * mm, f"Doctor: {provider_info.get('doctor_name', '')}, {provider_info.get('doctor_title', '')}")

    # Horizontal line under header
    pdf.line(left_margin, top_margin - 35 * mm, width - left_margin, top_margin - 35 * mm)

    # --- Prescription Body ---
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left_margin, top_margin - 45 * mm, "Patient Name: ___________________________")
    
    pdf.setFont("Helvetica-Bold", 12)  # Bold font for the "Date" label
    pdf.drawString(left_margin, top_margin - 55 * mm, "Date: ")  # Label 'Date'

    pdf.setFont("Helvetica", 12)  # Regular font for the date itself
    pdf.drawString(left_margin + 30 * mm, top_margin - 55 * mm, today_date_str)  # Insert the current date

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(left_margin, top_margin - 75 * mm, "Rx:")


    y_position = 90


    # Loop through the medications in the JSON file
    for prescription in prescription_data:
        medication = prescription.get("medication", "Unknown")
        dosage = prescription.get("dosage", "Unknown")
        frequency = prescription.get("frequency", "Unknown")
        notes = prescription.get("notes", "None")

        # Format the prescription details
        text_1 = f"{medication} - Dosage: {dosage}, Frequency: {frequency}"



        pdf.setFont("Helvetica", 12)
        pdf.drawString(left_margin + 10 * mm, top_margin - (y_position+5)* mm, text_1)


        text_2 = f"Notes: {notes}"

        pdf.setFont("Helvetica", 12)
        pdf.drawString(left_margin + 10 * mm, top_margin -(y_position+10)* mm, text_2)


        y_position = y_position + 15  # Move down for the next line


    # --- Footer Section ---
    pdf.line(left_margin, 50 * mm, width - left_margin, 50 * mm)
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(left_margin, 35 * mm, f"Signature: ___________________________")

    pdf.setFont("Helvetica-Oblique", 8)
    pdf.drawRightString(width - left_margin, 25 * mm, "This document was generated electronically.")

    # Save PDF
    pdf.save()
    print(f"✅ Prescription PDF created successfully: {output_pdf}")


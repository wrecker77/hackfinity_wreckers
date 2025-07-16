import streamlit as st
import os
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile
import requests
import time
from deep_translator import GoogleTranslator
from fpdf import FPDF
from cohere_product_pipeline import process_user_input
from pre_processing1 import categorize_products_with_cohere, refine_product_json, process_user_input
from json_file_gen import make_file   
from app import render
from generator import generate_pdf_from_json
# ------------------- Config ------------------- #
st.set_page_config(page_title="🎤 AI Product Catalog Assistant", layout="centered")

# ------------------- Session State ------------------- #
if "product_inputs" not in st.session_state:
    st.session_state.product_inputs = []
if "transcribed_input" not in st.session_state:
    st.session_state.transcribed_input = ""
if "audio_path" not in st.session_state:
    st.session_state.audio_path = None
if "catalog_data" not in st.session_state:
    st.session_state.catalog_data = []

# ------------------- AssemblyAI Setup ------------------- #
ASSEMBLYAI_API_KEY = "b6e4bad374774de0934049a037d79e2b"
HEADERS = {"authorization": ASSEMBLYAI_API_KEY}
UPLOAD_ENDPOINT = "https://api.assemblyai.com/v2/upload"
TRANSCRIBE_ENDPOINT = "https://api.assemblyai.com/v2/transcript"

# ------------------- Audio Functions ------------------- #
def record_audio(duration=8, samplerate=16000):
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wav.write(tmp_file.name, samplerate, (audio * 32767).astype(np.int16))
    return tmp_file.name

def upload_to_assemblyai(audio_path):
    with open(audio_path, "rb") as f:
        response = requests.post(UPLOAD_ENDPOINT, headers=HEADERS, data=f)
    response.raise_for_status()
    return response.json()["upload_url"]

def transcribe_audio(audio_url):
    payload = {"audio_url": audio_url, "language_detection": True}
    response = requests.post(TRANSCRIBE_ENDPOINT, headers=HEADERS, json=payload)
    response.raise_for_status()
    transcript_id = response.json()["id"]
    while True:
        poll = requests.get(f"{TRANSCRIBE_ENDPOINT}/{transcript_id}", headers=HEADERS)
        status = poll.json()["status"]
        if status == "completed":
            return poll.json()["text"]
        elif status == "error":
            raise RuntimeError(poll.json()["error"])
        time.sleep(2)

def translate_to_english(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except:
        return text

# ------------------- PDF Catalog Generator ------------------- #
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Product Catalog", ln=True, align='C')
    pdf.ln(10)
    for item in data:
        lines = item['description'].split('\n')
        for line in lines:
            pdf.multi_cell(0, 8, txt=line.strip())
        pdf.ln(5)
    pdf_output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(pdf_output.name)
    return pdf_output.name

# ------------------- UI ------------------- #
st.title("🧠 Immersive AI Catalog Builder")
st.write("Input your product description below using text or voice. Add multiple products before generating the catalog.")

# Text input with recording buttons
text_col, start_col, stop_col = st.columns([6, 1, 1])
with text_col:
    user_input = st.text_input("Describe your product", value=st.session_state.transcribed_input)
with start_col:
    if st.button("🎙️ Start"):
        st.session_state.audio_path = record_audio()
        st.success("🎧 Recorded 6 seconds")
with stop_col:
    if st.button("⏹️ Stop"):
        if st.session_state.audio_path:
            try:
                url = upload_to_assemblyai(st.session_state.audio_path)
                raw_text = transcribe_audio(url)
                translated = translate_to_english(raw_text)
                st.session_state.transcribed_input = translated
                st.success(f"📝 Transcribed: {translated}")
                os.remove(st.session_state.audio_path)
            except Exception as e:
                st.error(f"❌ {e}")

# Add product button
if st.button("➕ Add Product"):
    final_input = user_input.strip() or st.session_state.transcribed_input.strip()
    if final_input:
        st.session_state.product_inputs.append(final_input)
        st.session_state.transcribed_input = ""
        st.success("✅ Product Added")
    else:
        st.warning("Please enter or record something before adding.")

# Show added products
if st.session_state.product_inputs:
    st.markdown("---")
    st.markdown("### ✅ Products Added")
    for i, p in enumerate(st.session_state.product_inputs, 1):
        st.markdown(f"**{i}.** {p}")

# Generate Catalog Button
if st.button("✨ Generate Catalog"):
    if st.session_state.product_inputs:
        with st.spinner("🧠 Processing your product entries..."):
            try:
                # Join all raw entries from the UI
                results= process_user_input(" ".join(st.session_state.product_inputs))
                products = ""
                filetered_list = {}
                for i in range(0,len(results)):
                    products=products + str(i+1) + "." + results[i]["product name"] + ","
                    filetered_list[results[i]["product name"]] = results[i]["description"]
                catogories = categorize_products_with_cohere(products)
                json_output = []
                for k in list(catogories):
                    json_output.append({"category name": k ,"products":[refine_product_json({"product name":i,"description":filetered_list[i]}) for i in catogories[k]]})
                make_file(json_output,"catalog.json")
                render()
                generate_pdf_from_json("catalog.json")
            finally:
                print("error99999")
            

    else:
        st.warning("🚨 Add at least one product before generating.")
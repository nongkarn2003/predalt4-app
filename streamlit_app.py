import streamlit as st
import google.generativeai as genai

# Configure the Gemini API key
genai.configure(api_key="AIzaSyDgNonoLpFLupDqOs2TlCl7aoXs3yHCw1E")

# Load the Gemini model
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# Create the Streamlit application
st.title("ภาษาแปล")

# Select the target language
target_language = st.selectbox("เลือกภาษาปลายทาง", ["ไทย", "อังกฤษ", "เกาหลี", "ญี่ปุ่น"])

# Get the input text to translate
input_text = st.text_input("ป้อนข้อความที่ต้องการแปล: ")

# Construct the prompt for the Gemini model
prompt = f"แปลข้อความต่อไปนี้เป็นภาษา {target_language} {input_text}"

# Display the prompt
st.text(prompt)

# Translate the text when the "แปล" button is clicked
if st.button("แปล"):
    try:
        # Generate the translation using the Gemini model
        response = model.generate_content(prompt)

        # Display the translated text
        st.text(response.text)
    except Exception as e:
        # Handle any exceptions that occur during translation
        st.text(f"เกิดข้อผิดพลาด: {e}")

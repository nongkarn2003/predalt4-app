import streamlit as st
import google.generativeai as genai

# Configure the Gemini API key (assuming you have one)
genai.configure(api_key="AIzaSyDgNonoLpFLupDqOs2TlCl7aoXs3yHCw1E")

# Load the Gemini model
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# Create the Streamlit application
st.title("ภาษาแปลและข้อมูลหุ้น")

# Stock Market Input
stock_input = st.text_input("ป้อนชื่อหุ้นหรือรหัส (เช่น AAPL, AMZN): ")

# Process User Queries
if stock_input:
  # Craft a prompt for the Gemini API based on the user input
  prompt = f"สรุปข้อมูลเกี่ยวกับ {stock_input} ในช่วงที่ผ่านมา"

  # Generate response using the Gemini model
  response = model.generate_content(prompt)

  # Display the generated response
  st.text(response.text)

# Existing code for translation functionality (replace "..." with your code)
# ...


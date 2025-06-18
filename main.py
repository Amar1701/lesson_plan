import streamlit as st
from fpdf import FPDF
import requests
import re

# ✅ Groq API Setup
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama3-70b-8192"

# ✅ Function to remove emojis from prompt and response
def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002500-\U00002BEF"  # chinese
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

# ✅ Function to query Groq
def generate_lesson(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a knowledgeable teacher assistant that generates full, teachable lesson content from and beyond textbooks."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=data)
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return remove_emojis(content)

# ✅ Generate clean PDF (no emojis)
from unidecode import unidecode

def generate_pdf(text, filename="lesson_plan.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Remove emojis and convert special unicode to ASCII
    clean_text = remove_emojis(text)
    clean_text = unidecode(clean_text)

    for line in clean_text.split('\n'):
        pdf.multi_cell(0, 10, line)

    pdf.output(filename)
    return filename


# ✅ Streamlit UI
st.set_page_config(page_title="AI Lesson Planner", layout="wide")
st.title("🧑‍🏫 AI-Powered Lesson Content Generator")

with st.form("lesson_form"):
    lesson_title = st.text_input("🔤 Lesson Title")
    grade = st.text_input("🎓 Grade/Class (e.g., Class 7)")
    subject = st.text_input("📚 Subject (e.g., Science)")
    board = st.selectbox("🏫 Board", ["Tamil Nadu", "CBSE", "ICSE", "Other"])
    notes = st.text_area("📌 Any additional notes or focus areas?")
    submit = st.form_submit_button("🚀 Generate Full Content")

if submit:
    with st.spinner("Generating full content to teach..."):
        prompt = f"""
You are an expert teacher. Generate a complete, detailed explanation suitable for teaching in class for the following:

Lesson Title: {lesson_title}
Grade/Class: {grade}
Subject: {subject}
Board: {board}
Focus: Teach the topic fully, not just key points — explain both within and beyond the textbook scope in detail.

Additional Notes: {notes}

Avoid using emojis or symbols. Provide clear, academic explanation in plain text.
"""
        try:
            full_content = generate_lesson(prompt)
            st.success("✅ Full lesson content generated!")
            st.markdown("### 📄 Generated Content")
            st.write(full_content)

            pdf_path = generate_pdf(full_content)
            with open(pdf_path, "rb") as f:
                st.download_button("📥 Download PDF", f, file_name="lesson_plan.pdf", mime="application/pdf")

        except Exception as e:
            st.error(f"❌ Error: {e}")

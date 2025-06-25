import streamlit as st
import requests
from fpdf import FPDF
from io import BytesIO

# ------------------------ CONFIG ------------------------
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-70b-8192"

# -------------------- RECOMMENDER -----------------------
def recommend_topics(topic):
    related_topics = {
        "Friction": ["Newton's Laws", "Types of Forces", "Motion", "Gravitational Force"],
        "Photosynthesis": ["Respiration", "Chloroplast", "Food Chain", "Plant Cells"],
        "Electricity": ["Current", "Circuits", "Ohm's Law", "Magnetic Effects"],
        "Decimals": ["Fractions", "Place Value", "Percentages", "Measurements"]
    }
    return related_topics.get(topic, ["Explore related topics in your syllabus!"])

# -------------------- PROMPT TEMPLATE -------------------
def build_prompt(topic, grade, board, language, length):
    return f"""
You are an intelligent AI-powered educational assistant helping school teachers prepare structured lesson content.

🎯 Task:
Generate a comprehensive lesson content on the topic "{topic}" for {grade}, following the {board} syllabus. Tailor the content complexity appropriately:
- Basic and intuitive for lower grades (Class 1–5)
- Foundational and relatable for middle grades (Class 6–8)
- Concept-rich and exam-oriented for higher grades (Class 9–12)

📏 Content Length:
The expected length is {length}.

📘 Include the following sections:
1. ✅ Concept Explanation – Syllabus-aligned, clear and structured.
2. 🎲 Playful Explanation – A fun or real-world analogy/story to explain the concept.
3. 🧪 Activity – At least one hands-on or thought-based classroom/home activity.
4. 🧠 Challenge or Reflection – A single deep-thinking question for the student.
5. 📋 Summary – A simple recap of key points in 4–5 bullet points.

🗂 Output Format:
- Do not include lesson plan structure like “Period 1” or “Assessment”.
- Do not write teacher tips or planning instructions.
- Do not include external web links.
- Format the output cleanly with section headers and paragraph breaks.

🌐 Language: {language}

Your goal is to produce a ready-to-use, well-written lesson content suitable for classroom teaching and printable in a PDF format.
"""

# ------------------- GROQ API CALL ----------------------
def get_lesson_content(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    response = requests.post(GROQ_API_URL, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"❌ Error from Groq API: {response.status_code} - {response.text}"

# ------------------ PDF GENERATION ----------------------
def generate_pdf_buffer(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_auto_page_break(auto=True, margin=15)

    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)

    # Export PDF as string (binary) and encode
    pdf_output = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_output)
# --------------------- STREAMLIT UI ---------------------
def main():
    st.set_page_config(page_title="AI Lesson Planner", layout="centered")
    st.title("📚 AI Lesson Planner")
    st.markdown("Generate grade-wise, syllabus-aligned lesson content with one click!")

    with st.form("lesson_form"):
        topic = st.text_input("📌 Topic", placeholder="e.g., Friction")
        grade = st.selectbox("🏫 Class", [f"Class {i}" for i in range(1, 13)])
        board = st.selectbox("📚 Board", ["TN State Board", "NCERT", "ICSE"])
        language = st.selectbox("🌐 Language", ["English", "Tamil"])
        length = st.selectbox("📝 Content Length", ["Short Summary", "1 Page", "Long Explanation"])

        submitted = st.form_submit_button("Generate Lesson")

    if submitted:
        with st.spinner("🧠 Generating lesson content..."):
            prompt = build_prompt(topic, grade, board, language, length)
            lesson_content = get_lesson_content(prompt)
            recommendations = recommend_topics(topic)

        st.subheader("📘 Lesson Content")
        st.markdown(lesson_content)

        st.subheader("📌 What to Learn Next")
        for rec in recommendations:
            st.markdown(f"- {rec}")

        with st.spinner("📦 Preparing your PDF..."):
            pdf_buffer = generate_pdf_buffer(lesson_content)
            st.download_button(
                label="📥 Download PDF",
                data=pdf_buffer,
                file_name="lesson.pdf",
                mime="application/pdf"
            )

        st.success("✅ Lesson generated successfully!")

# ------------------------ RUN APP -----------------------
if __name__ == "__main__":
    main()

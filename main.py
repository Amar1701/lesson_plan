# AI Lesson Planner 2.0 – Dynamic Subjects + Second Language Support

import streamlit as st
import requests
from fpdf import FPDF
from io import BytesIO
import re

# ------------------------ CONFIG ------------------------
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-70b-8192"

# -------------------- CLASS-SUBJECT MAPPING ------------------------
class_subjects = {
    "Class 1": ["English", "Maths", "EVS"],
    "Class 2": ["English", "Maths", "EVS"],
    "Class 3": ["English", "Maths", "EVS"],
    "Class 4": ["English", "Maths", "EVS"],
    "Class 5": ["English", "Maths", "Science", "Social Science"],
    "Class 6": ["English", "Maths", "Science", "Social Science", "Tamil", "Hindi"],
    "Class 7": ["English", "Maths", "Science", "Social Science", "Tamil", "Hindi"],
    "Class 8": ["English", "Maths", "Science", "Social Science", "Tamil", "Hindi"],
    "Class 9": ["English", "Maths", "Science", "Social Science", "Tamil", "Hindi"],
    "Class 10": ["English", "Maths", "Science", "Social Science", "Tamil", "Hindi"],
    "Class 11": ["Physics", "Chemistry", "Biology", "Mathematics", "Computer Science", "Accountancy", "Economics", "Business Studies", "History", "Geography", "Political Science"],
    "Class 12": ["Physics", "Chemistry", "Biology", "Mathematics", "Computer Science", "Accountancy", "Economics", "Business Studies", "History", "Geography", "Political Science"]
}

# -------------------- UTILITIES ------------------------
def clean_text(text):
    def is_latin1(char):
        return ord(char) <= 255
    return ''.join(c for c in text if is_latin1(c))

class LessonPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "AI Lesson Planner", ln=True, align='C')
        self.ln(5)

    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.multi_cell(0, 10, title)
        self.ln(1)

    def chapter_body(self, body):
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 8, body)
        self.ln()

def generate_pdf_buffer(text):
    text = clean_text(text)
    pdf = LessonPDF()
    pdf.add_page()
    sections = re.split(r"\*\*(.*?)\\*\\*", text)
    for i in range(1, len(sections), 2):
        pdf.chapter_title(sections[i].strip())
        pdf.chapter_body(sections[i+1].strip())
    pdf_output = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_output)

def generate_assessment_pdf(content):
    text = clean_text(content)
    pdf = LessonPDF()
    pdf.add_page()
    pdf.chapter_title("Assessment Questions")
    sections = re.split(r"\*\*(.*?)\\*\\*", text)
    for i in range(1, len(sections), 2):
        pdf.chapter_title(sections[i].strip())
        pdf.chapter_body(sections[i+1].strip())
    pdf_output = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_output)

# -------------------- YOUTUBE ------------------------
def get_youtube_videos(topic):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": topic + " Indian students",
        "key": YOUTUBE_API_KEY,
        "maxResults": 3,
        "type": "video",
        "safeSearch": "strict",
        "regionCode": "IN"
    }
    res = requests.get(url, params=params)
    items = res.json().get("items", [])
    return [(v["snippet"]["title"], "https://www.youtube.com/watch?v=" + v["id"]["videoId"]) for v in items]

# -------------------- PROMPTS ------------------------
def build_lesson_prompt(topic, grade, board, language, length):
    if language.lower() == 'tamil':
        return f"""
நீங்கள் அன்பும் அறிவும் நிறைந்த AI ஆசிரியர்.

🎯 பணிகள்:
"{topic}" என்ற தலைப்பில் {grade} வகுப்பு மாணவர்களுக்காக {board} பாடத்திட்டத்தின் அடிப்படையில் ஒரு விளக்கமான பாடத்திட்டத்தை உருவாக்கவும்.
சரியான சூத்திரங்கள், உருவகங்கள் மற்றும் மாணவர்களுக்கு நட்பான உதாரணங்களை அளிக்கவும்.

📘 பிரிவுகள்:
1. **கருத்து விளக்கம்**
2. **ஏன் இது முக்கியம்**
3. **ஒரு கதையோ உருவகமோ**
4. **நீங்களே முயற்சி செய்யுங்கள்**
5. **பொதுவான சந்தேகங்கள்**
6. **சவால் கேள்வி**
7. **சுருக்கம்**

மொழி: {language}
உள்ளடக்க நீளம்: {length}
"""
    elif language.lower() == 'hindi':
        return f"""
आप एक दयालु और बुद्धिमान AI शिक्षक हैं।

🎯 कार्य:
\"{topic}\" पर {grade} छात्रों के लिए {board} बोर्ड का अनुसरण करते हुए एक अच्छी तरह से समझाया गया पाठ तैयार करें।
वास्तविक सूत्र, उपमाएँ और छात्रों के अनुकूल उदाहरण शामिल करें।

📘 अनुभाग:
1. **संकल्पना व्याख्या**
2. **यह क्यों महत्वपूर्ण है**
3. **कहानी या उपमा**
4. **स्वयं प्रयास करें**
5. **आम शंकाएँ**
6. **चुनौती प्रश्न**
7. **सारांश**

भाषा: {language}
सामग्री की लंबाई: {length}
"""
    else:
        return f"""
You are a kind and intelligent AI teacher.

🎯 Task:
Create a well-explained lesson on "{topic}" for {grade} students following the {board} board.
Include real formulas (if applicable), analogies, student-friendly language, and examples.

📘 Sections:
1. **Concept Explanation**
2. **Why It Matters**
3. **Analogy or Story**
4. **Try It Yourself**
5. **Common Doubts**
6. **Challenge Question**
7. **Summary**

Language: {language}
Content Length: {length}
"""

def build_mcq_prompt(topic, level, count):
    return f"""
Create {count} multiple-choice questions on the topic "{topic}".
- Categorize them under **{level}** difficulty.
- Each question should have 4 options (A, B, C, D)
- Highlight the correct option.
- At the end, include an Answer Key section with explanations.
"""

# -------------------- API CALL ----------------------
def get_lesson_content(prompt):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    data = {"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
    res = requests.post(GROQ_API_URL, headers=headers, json=data)
    return res.json()['choices'][0]['message']['content'] if res.status_code == 200 else f"Error: {res.text}"

# -------------------- STREAMLIT ---------------------
def main():
    st.set_page_config(page_title="AI Lesson Planner", layout="centered")
    st.title("📚 AI Lesson Planner")

    if 'lesson_content' not in st.session_state:
        st.session_state.lesson_content = ""
        st.session_state.assessment_content = ""
        st.session_state.youtube_videos = []

    board = st.selectbox("📚 Board", ["TN State Board", "NCERT", "ICSE"])
    grade = st.selectbox("🏫 Class", list(class_subjects.keys()))
    subjects = class_subjects.get(grade, [])
    subject = st.selectbox("📖 Subject", subjects)

    topic = st.text_input("📌 Topic", placeholder="e.g., Laws of Motion")
    language = st.selectbox("🌐 Language", ["English", "Tamil", "Hindi"])
    length = st.selectbox("📝 Content Length", ["Short Summary", "1 Page", "Long Explanation"])

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📄 Generate Lesson Content") and topic:
            with st.spinner("Generating lesson content..."):
                prompt = build_lesson_prompt(topic, grade, board, language, length)
                st.session_state.lesson_content = get_lesson_content(prompt)
                st.session_state.youtube_videos = get_youtube_videos(topic)

    with col2:
        difficulty = st.radio("Select Difficulty Level", ["Easy", "Medium", "Hard"], horizontal=True, key="difficulty")
        question_count = st.radio("Number of Questions", [10, 25], horizontal=True, key="qcount")

        if st.button("🧠 Generate Assessment") and topic:
            with st.spinner("Generating assessment questions..."):
                prompt = build_mcq_prompt(topic, difficulty, question_count)
                st.session_state.assessment_content = get_lesson_content(prompt)

    if st.session_state.lesson_content:
        st.subheader("📘 Lesson Content")
        st.markdown(st.session_state.lesson_content)

        if st.session_state.youtube_videos:
            st.subheader("▶️ Relevant YouTube Videos (India)")
            for title, link in st.session_state.youtube_videos:
                st.markdown(f"[🎥 {title}]({link})")

        pdf_buffer = generate_pdf_buffer(st.session_state.lesson_content)
        st.download_button("📥 Download Lesson PDF", data=pdf_buffer, file_name="lesson.pdf", mime="application/pdf")

    if st.session_state.assessment_content:
        st.subheader("📋 Assessment Preview")
        st.markdown(st.session_state.assessment_content)
        pdf_buffer = generate_assessment_pdf(st.session_state.assessment_content)
        st.download_button("📥 Download Assessment PDF", data=pdf_buffer, file_name="assessment.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()

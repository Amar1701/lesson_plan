# AI Lesson Planner 2.0 with Human-like Teaching, Voice Input, YouTube, PDF Export

import streamlit as st
import requests
from fpdf import FPDF
from io import BytesIO
import re
import speech_recognition as sr

# ------------------------ CONFIG ------------------------
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-70b-8192"

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

def generate_pdf_buffer(text, youtube_links):
    text = clean_text(text)
    pdf = LessonPDF()
    pdf.add_page()
    sections = re.split(r"\*\*(.*?)\*\*", text)
    for i in range(1, len(sections), 2):
        pdf.chapter_title(sections[i].strip())
        pdf.chapter_body(sections[i+1].strip())

    if youtube_links:
        pdf.chapter_title("YouTube Video Recommendations")
        for title, link in youtube_links:
            pdf.chapter_body(f"{title}\n{link}")

    pdf_output = pdf.output(dest='S').encode('latin1')
    return BytesIO(pdf_output)

# -------------------- YOUTUBE ------------------------
def get_youtube_videos(topic):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": topic + " for students",
        "key": YOUTUBE_API_KEY,
        "maxResults": 3,
        "type": "video",
        "safeSearch": "strict"
    }
    res = requests.get(url, params=params)
    items = res.json().get("items", [])
    return [(v["snippet"]["title"], "https://www.youtube.com/watch?v=" + v["id"]["videoId"]) for v in items]

# -------------------- SPEECH TO TEXT ------------------
def speech_to_text():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Please speak now...")
        audio = r.listen(source)
        try:
            return r.recognize_google(audio)
        except sr.UnknownValueError:
            st.warning("Could not understand audio")
        except sr.RequestError:
            st.error("Speech Recognition API error")
    return ""

# -------------------- PROMPT ------------------------
def build_prompt(topic, grade, board, language, length):
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

# -------------------- GROQ API ----------------------
def get_lesson_content(prompt):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    data = {"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
    res = requests.post(GROQ_API_URL, headers=headers, json=data)
    return res.json()['choices'][0]['message']['content'] if res.status_code == 200 else f"Error: {res.text}"

# -------------------- STREAMLIT ---------------------
def main():
    st.set_page_config(page_title="AI Lesson Planner", layout="centered")
    st.title("📚 AI Lesson Planner – Human-Style Teaching")

    if 'lesson_content' not in st.session_state:
        st.session_state.lesson_content = ""
        st.session_state.youtube_videos = []
        st.session_state.topic_input = ""

    use_mic = st.checkbox("🎙️ Use microphone for topic input")

    topic = ""
    if use_mic:
        if st.button("🎤 Speak Now"):
            topic = speech_to_text()
            st.session_state.topic_input = topic
            st.success(f"Recognized topic: {topic}")
        else:
            topic = st.session_state.topic_input
    else:
        topic = st.text_input("📌 Topic", placeholder="e.g., Friction")

    grade = st.selectbox("🏫 Class", [f"Class {i}" for i in range(1, 13)])
    board = st.selectbox("📚 Board", ["TN State Board", "NCERT", "ICSE"])
    language = st.selectbox("🌐 Language", ["English"])
    length = st.selectbox("📝 Content Length", ["Short Summary", "1 Page", "Long Explanation"])

    if st.button("🚀 Generate Lesson") and topic:
        with st.spinner("Thinking like a great teacher..."):
            prompt = build_prompt(topic, grade, board, language, length)
            lesson_content = get_lesson_content(prompt)
            youtube_videos = get_youtube_videos(topic)
            st.session_state.lesson_content = lesson_content
            st.session_state.youtube_videos = youtube_videos

    if st.session_state.lesson_content:
        st.subheader("📘 Lesson Content")
        st.markdown(st.session_state.lesson_content)

        st.subheader("▶️ YouTube Videos")
        for title, link in st.session_state.youtube_videos:
            st.markdown(f"[🎥 {title}]({link})")

        with st.spinner("📄 Generating PDF..."):
            pdf_buffer = generate_pdf_buffer(st.session_state.lesson_content, st.session_state.youtube_videos)
            st.download_button("📥 Download as PDF", data=pdf_buffer, file_name="lesson.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()


    # ✅ This must be the first Streamlit command
import streamlit as st
st.set_page_config(page_title="NL2SQL with Google Generative AI")

# ✅ Other imports
'''
from dotenv import load_dotenv
from pathlib import Path
'''
import os

import sqlite3
import google.generativeai as genai
import time
from datetime import datetime, timedelta

'''
# ✅ Load .env
dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path, override=True)

# ✅ Load API key
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("API key not found. Please add it to your .env file as GOOGLE_API_KEY.")
    st.stop()

    '''

# ✅ Load API key from Streamlit secrets
API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=API_KEY)


# ✅ Initialize session state for rate limiting
if 'last_request_time' not in st.session_state:
    st.session_state.last_request_time = None
if 'request_count' not in st.session_state:
    st.session_state.request_count = 0
if 'request_history' not in st.session_state:
    st.session_state.request_history = []

# ✅ Rate limiting function
def check_rate_limit():
    """Check if we can make a request based on rate limits"""
    now = datetime.now()
    
    # Clean old requests (older than 1 minute)
    st.session_state.request_history = [
        req_time for req_time in st.session_state.request_history 
        if now - req_time < timedelta(minutes=1)
    ]
    
    # Check if we've exceeded 15 requests per minute (free tier limit)
    if len(st.session_state.request_history) >= 15:
        return False, "Rate limit exceeded. Please wait a minute before making another request."
    
    # Check if we need to wait between requests (minimum 4 seconds)
    if st.session_state.last_request_time:
        time_since_last = now - st.session_state.last_request_time
        if time_since_last < timedelta(seconds=4):
            wait_time = 4 - time_since_last.total_seconds()
            return False, f"Please wait {wait_time:.1f} seconds before making another request."
    
    return True, "OK"

# ✅ Optional: Show API key in sidebar
with st.sidebar:
    st.markdown("### 🔐 Debug Info")
    #st.code(f"API Key: {API_KEY[:8]}...{API_KEY[-5:]}", language="text")
    st.markdown("### 📊 Rate Limiting")
    st.write(f"Requests in last minute: {len(st.session_state.request_history)}/15")
    if st.session_state.last_request_time:
        time_since_last = datetime.now() - st.session_state.last_request_time
        st.write(f"Time since last request: {time_since_last.total_seconds():.1f}s")

# ✅ Functions
def get_genai_response(question, prompt):
    try:
        # Use correct model name - gemini-1.5-flash (NOT 1.0)
        model = genai.GenerativeModel('gemini-1.5-flash-8b')
        response = model.generate_content(prompt + "\n\nQuestion: " + question)
        
        # Update rate limiting tracking
        now = datetime.now()
        st.session_state.request_history.append(now)
        st.session_state.last_request_time = now
        
        return response.text.strip()
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            return "❌ Rate limit exceeded. Please wait a minute and try again."
        elif "403" in error_msg:
            return "❌ API key invalid or billing not enabled. Please check your Google Cloud project."
        else:
            return f"❌ Error: {error_msg}"

def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        conn.commit()
    except Exception as e:
        rows = [("Error", str(e))]
    conn.close()
    return rows

prompt = """
You are an expert NL2SQL model. Your task is to accurately convert English questions into valid SQL queries.

Understand the intent behind natural language questions.

Identify relevant tables, columns, conditions, and relationships.

Use appropriate SQL syntax (e.g., SELECT, JOIN, WHERE, GROUP BY, ORDER BY, etc.).

Ensure the output SQL query is syntactically correct and logically matches the meaning of the input question.

Handle edge cases, such as missing conditions, ambiguous phrasing, or multi-table joins.

Prefer readability and accuracy. Comment the query when appropriate.
The database has the following tables and relationships:

STUDENT: STUDENT_ID, NAME, EMAIL, PHONE, ADDRESS, DATE_OF_BIRTH, ADMISSION_DATE, CLASS, SECTION, SEMESTER, GPA, DEPT_ID, STATUS

DEPARTMENTS: DEPT_ID, DEPT_NAME, DEPT_HEAD, BUILDING, BUDGET

INSTRUCTORS: INSTRUCTOR_ID, INSTRUCTOR_NAME, DEPT_ID, EMAIL, PHONE, HIRE_DATE, SALARY

COURSES: COURSE_ID, COURSE_NAME, COURSE_CODE, CREDITS, DEPT_ID, INSTRUCTOR_ID, SEMESTER, YEAR, MAX_STUDENTS

ENROLLMENTS: ENROLLMENT_ID, STUDENT_ID, COURSE_ID, ENROLLMENT_DATE, GRADE, MARKS, ATTENDANCE_PERCENTAGE, STATUS

Examples:
Q: How many students are there?
A: SELECT COUNT(*) FROM STUDENT;

Q: Show all students in Data Science department
A: SELECT s.* FROM STUDENT s JOIN DEPARTMENTS d ON s.DEPT_ID = d.DEPT_ID WHERE d.DEPT_NAME = "Data Science";

Q: What courses is Krish Naik taking?
A: SELECT c.COURSE_NAME FROM STUDENT s JOIN ENROLLMENTS e ON s.STUDENT_ID = e.STUDENT_ID JOIN COURSES c ON e.COURSE_ID = c.COURSE_ID WHERE s.NAME = "Krish Naik";

Q: Show students with GPA greater than 3.5
A: SELECT NAME, GPA FROM STUDENT WHERE GPA > 3.5;

Q: Average marks by department
A: SELECT d.DEPT_NAME, AVG(e.MARKS) FROM DEPARTMENTS d JOIN STUDENT s ON d.DEPT_ID = s.DEPT_ID JOIN ENROLLMENTS e ON s.STUDENT_ID = e.STUDENT_ID GROUP BY d.DEPT_NAME;

Q: Which instructor teaches the most courses?
A: SELECT i.INSTRUCTOR_NAME, COUNT(c.COURSE_ID) as course_count FROM INSTRUCTORS i JOIN COURSES c ON i.INSTRUCTOR_ID = c.INSTRUCTOR_ID GROUP BY i.INSTRUCTOR_NAME ORDER BY course_count DESC LIMIT 1;

Important: Return only the SQL query without any markdown formatting, explanations, or the word 'SQL'.
"""

# ✅ UI
st.title("🧠 Natural Language to SQL")
st.write("Enter your question in plain English and get SQL results from the STUDENT database.")

# Add rate limiting warning
st.info("⚠️ Free tier limit: 15 requests/minute. Please wait 4 seconds between requests.")

question = st.text_input("🔍 Your Question in English:")
submit = st.button("Submit")

if submit:
    if not question:
        st.warning("Please enter a question.")
    else:
        # Check rate limits
        can_proceed, message = check_rate_limit()
        
        if not can_proceed:
            st.error(message)
        else:
            with st.spinner("Generating SQL query..."):
                sql_query = get_genai_response(question, prompt)
                
            st.subheader("🧾 Generated SQL")
            st.code(sql_query)
            
            # Only execute SQL if generation was successful
            if not sql_query.startswith("❌"):
                st.subheader("📊 SQL Result")
                result = read_sql_query(sql_query, "student.db")
                for row in result:
                    st.write(row)
            else:
                st.error("SQL generation failed. Please try again later.")

# ✅ Additional troubleshooting info
with st.expander("🔧 Troubleshooting"):
    st.markdown("""
    **Common Issues:**
    1. **Rate Limit Exceeded**: Free tier allows 15 requests/minute. Wait 1 minute.
    2. **API Key Issues**: Make sure your key is valid and billing is enabled.
    3. **Model Issues**: We're using `gemini-1.5-flash` which has better rate limits.
    
    **Solutions:**
    - Enable billing in Google Cloud Console for higher limits
    - Wait between requests (4+ seconds recommended)
    - Use a different model if needed
    """)
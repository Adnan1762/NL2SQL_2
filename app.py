# ✅ This must be the first Streamlit command
import streamlit as st
st.set_page_config(page_title="NL2SQL with Generative AI", layout="wide")

# ✅ Other imports
from dotenv import load_dotenv
from pathlib import Path
import os
import sqlite3
import google.generativeai as genai
import time
import pandas as pd
from datetime import datetime, timedelta

# ✅ Load .env
dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path, override=True)

# ✅ Load API key
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("API key not found. Please add it to your .env file as GOOGLE_API_KEY.")
    st.stop()

genai.configure(api_key=API_KEY)

# ✅ Initialize session state for rate limiting
if 'last_request_time' not in st.session_state:
    st.session_state.last_request_time = None
if 'request_count' not in st.session_state:
    st.session_state.request_count = 0
if 'request_history' not in st.session_state:
    st.session_state.request_history = []

# ✅ Database functions
def get_table_structure(db_path="student.db"):
    """Get information about table structure only - no actual data"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        
        table_structure = {}
        for table in tables:
            # Get column information with types and constraints
            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()
            
            # Get foreign key information
            cursor.execute(f"PRAGMA foreign_key_list({table});")
            foreign_keys = cursor.fetchall()
            
            # Get index information (to identify additional keys)
            cursor.execute(f"PRAGMA index_list({table});")
            indexes = cursor.fetchall()
            
            # Get row count only (no actual data)
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            row_count = cursor.fetchone()[0]
            
            table_structure[table] = {
                'columns': columns,
                'foreign_keys': foreign_keys,
                'indexes': indexes,
                'row_count': row_count
            }
        
        conn.close()
        return table_structure
    except Exception as e:
        conn.close()
        return {}

def get_table_relationships(db_path="student.db"):
    """Get foreign key relationships between tables"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    relationships = []
    
    try:
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        
        for table in tables:
            # Get foreign key information
            cursor.execute(f"PRAGMA foreign_key_list({table});")
            foreign_keys = cursor.fetchall()
            
            for fk in foreign_keys:
                relationships.append({
                    'from_table': table,
                    'from_column': fk[3],  # from column
                    'to_table': fk[2],     # to table
                    'to_column': fk[4]     # to column
                })
    
    except Exception as e:
        pass
    
    conn.close()
    return relationships

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

# ✅ Functions
def get_genai_response(question, prompt):
    try:
        
        model = genai.GenerativeModel('gemini-2.0-flash')
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

# ✅ Sidebar with rate limiting info
with st.sidebar:
    st.markdown("### 🔐 Debug Info")
    st.markdown("### 📊 Rate Limiting")
    st.write(f"Requests in last minute: {len(st.session_state.request_history)}/15")
    if st.session_state.last_request_time:
        time_since_last = datetime.now() - st.session_state.last_request_time
        st.write(f"Time since last request: {time_since_last.total_seconds():.1f}s")

# ✅ Main UI
st.title("🧠 Natural Language to SQL")

# Create tabs
tab1, tab2 = st.tabs(["🔍 Query Database", "🏗️ Database Structure"])

with tab1:
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

with tab2:
    st.write("🔒 **Privacy-Safe Database Structure View** - Only table schemas are shown, no actual data is exposed.")
    
    try:
        table_structure = get_table_structure()
        
        if not table_structure:
            st.error("No database found. Please make sure 'student.db' exists in the same directory.")
        else:
            st.success(f"🗃️ Found {len(table_structure)} tables in the database")
            
            # Display database overview (structure only)
            st.subheader("📊 Database Overview")
            overview_data = []
            for table_name, info in table_structure.items():
                overview_data.append({
                    "Table": table_name.upper(),
                    "Columns": len(info['columns']),
                    "Records": info['row_count'],  # Just count, no actual data
                    "Primary Keys": len([col for col in info['columns'] if col[5]]),
                    "Foreign Keys": len(info['foreign_keys'])
                })
            
            overview_df = pd.DataFrame(overview_data)
            st.dataframe(overview_df, use_container_width=True)
            
            # Show table relationships
            st.subheader("🔗 Table Relationships")
            relationships = get_table_relationships()
            if relationships:
                rel_data = []
                for rel in relationships:
                    rel_data.append({
                        "From Table": rel['from_table'].upper(),
                        "From Column": rel['from_column'],
                        "To Table": rel['to_table'].upper(),
                        "To Column": rel['to_column'],
                        "Relationship": f"{rel['from_table']}.{rel['from_column']} → {rel['to_table']}.{rel['to_column']}"
                    })
                
                rel_df = pd.DataFrame(rel_data)
                st.dataframe(rel_df, use_container_width=True)
            else:
                st.info("No foreign key relationships found in the database.")
            
            # Create expandable sections for each table (structure only)
            st.subheader("🏗️ Table Structures")
            for table_name, info in table_structure.items():
                with st.expander(f"📋 {table_name.upper()} Table Structure", expanded=False):
                    
                    # Show column information with enhanced details
                    st.markdown("**📝 Column Information:**")
                    column_data = []
                    for col in info['columns']:
                        column_data.append({
                            "Column Name": col[1],
                            "Data Type": col[2],
                            "Primary Key": "✅ Yes" if col[5] else "❌ No",
                            "Not Null": "✅ Yes" if col[3] else "❌ No",
                            "Default Value": col[4] if col[4] else "None"
                        })
                    
                    column_df = pd.DataFrame(column_data)
                    st.dataframe(column_df, use_container_width=True)
                    
                    # Show foreign key relationships for this table
                    if info['foreign_keys']:
                        st.markdown("**🔗 Foreign Key Relationships:**")
                        fk_data = []
                        for fk in info['foreign_keys']:
                            fk_data.append({
                                "Column": fk[3],
                                "References Table": fk[2],
                                "References Column": fk[4],
                                "Relationship": f"{fk[3]} → {fk[2]}.{fk[4]}"
                            })
                        
                        fk_df = pd.DataFrame(fk_data)
                        st.dataframe(fk_df, use_container_width=True)
                    else:
                        st.info("No foreign key relationships for this table.")
                    
                    # Show record count and basic stats (no actual data)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Records", info['row_count'])
                    with col2:
                        st.metric("Total Columns", len(info['columns']))
    
    except Exception as e:
        st.error(f"Error loading database structure: {str(e)}")

# ✅ Additional troubleshooting info
with st.expander("🔧 Troubleshooting"):
    st.markdown("""
    **Common Issues:**
    1. **Rate Limit Exceeded**: Free tier allows 15 requests/minute. Wait 1 minute.
    2. **API Key Issues**: Make sure your key is valid and billing is enabled.
    3. **Model Issues**: We're using `gemini-1.5-flash` which has better rate limits.
    4. **Database Issues**: Make sure `student.db` exists in the same directory as the app.
    
    **Solutions:**
    - Enable billing in Google Cloud Console for higher limits
    - Wait between requests (4+ seconds recommended)
    - Use a different model if needed
    - Run the SQL script to create the database if it doesn't exist
    """)

# ✅ Database Schema Reference
with st.expander("📚 Database Schema Reference"):
    st.markdown("""
    **🏗️ Table Relationships:**
    
    - **STUDENT** → **DEPARTMENTS** (via DEPT_ID)
    - **INSTRUCTORS** → **DEPARTMENTS** (via DEPT_ID)
    - **COURSES** → **DEPARTMENTS** (via DEPT_ID)
    - **COURSES** → **INSTRUCTORS** (via INSTRUCTOR_ID)
    - **ENROLLMENTS** → **STUDENT** (via STUDENT_ID)
    - **ENROLLMENTS** → **COURSES** (via COURSE_ID)
    
    **📋 Table Descriptions:**
    - **STUDENT**: Student information including GPA, contact details, and department
    - **DEPARTMENTS**: Department details with budget and head information
    - **INSTRUCTORS**: Faculty information with salary and department assignment
    - **COURSES**: Course catalog with credits, capacity, and instructor assignment
    - **ENROLLMENTS**: Student-course relationships with grades and attendance
    
    **🔒 Privacy Note:** This structure view only shows table schemas and relationships. No actual data is displayed to protect privacy.
    """)

# ✅ Privacy and Security Notice
st.markdown("""
---
**🔒 Privacy & Security Notice:**
This application is designed with privacy in mind. The database structure view only shows:
- Table names and column structures
- Data types and constraints
- Primary and foreign key relationships
- Record counts (no actual data)

**No sensitive data is exposed** in the structure view to protect user privacy and data security.
""")
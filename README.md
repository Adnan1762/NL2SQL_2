
# 🧠 NL2SQL with Google Gemini & Streamlit

This project enables natural language queries to be translated into SQL using Google's Generative AI (Gemini),
allowing non-technical users to interact with a database seamlessly through a simple web interface built with Streamlit.



## 🚀 Features

- 🔄 Converts English questions into valid SQL queries using **Gemini 1.5 Flash**
- 🧾 Executes queries against a local **SQLite database**
- 📊 Displays real-time query results in a clean UI
- 🔒 Secure API key management using `.env`
- 📦 Lightweight and portable with minimal dependencies



## 🛠️ Tech Stack

- **Frontend/UI**: [Streamlit](https://streamlit.io/)
- **LLM Integration**: [Google Gemini API](https://ai.google.dev/)
- **Database**: SQLite
- **Language**: Python 3
- **Prompt Engineering**: Few-shot examples



## 📂 Project Structure
```
NL2SQL/
├── app.py # Main Streamlit application
├── sql.py # Creates the SQLite database and inserts dummy records
├── student.db # SQLite database (auto-generated)
├── .env # Stores your Google API key (excluded from Git)
├── req.txt # Python dependencies
├── venv/ # Virtual environment (excluded from Git)
└── .gitignore # Git exclusions
```

## ⚙️ Setup Instructions

1. **Clone the repository**
  


2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r req.txt
   ```

4. **Create a `.env` file**

   ```
   GOOGLE_API_KEY=your_google_gemini_api_key
   ```

5. **Initialize the database**

   ```bash
   python sql.py
   ```

6. **Run the app**

   ```bash
   streamlit run app.py
   ```



## 💡 Example Prompts

> "Show all students in Data Science."


![image](https://github.com/user-attachments/assets/eff6971b-07ff-4250-89a1-8d5c4ac8c678)


> "Show students with marks greater than 80."


![image](https://github.com/user-attachments/assets/4a0b2369-9f12-4dc0-8fc8-c528c650d392)




## 📌 Future Improvements

* ✅ Add support for more complex SQL queries (joins, aggregation)
* ✅ Deploy the app with Streamlit Cloud or Docker
* 🔍 Add unit tests for SQL validation
* 💾 Use a hosted database for scalability



## 📄 License

This project is licensed under the MIT License.




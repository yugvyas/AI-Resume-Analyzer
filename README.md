---

# **AI Resume Analyzer - Build Your Own AI-Powered Job Application Assistant! 🚀**  

## **Overview**  
The **AI Resume Analyzer** is an advanced application that compares resumes with job descriptions, highlights **matching & missing skills**, provides a **resume score**, and generates **AI-driven suggestions** to improve your chances of landing a job. 

Built with **Python, Streamlit, and Google Gemini AI**, this tool was customized and enhanced with additional analytics (`enhanced_analytics.py`) and extended logic beyond the base version I explored.  

---

## **Features**  
✅ Upload and analyze resumes in **PDF format**  
✅ Extract and process text using **PyMuPDF**  
✅ Compare resume content with job descriptions  
✅ Highlight **matching skills** and **gaps**  
✅ Generate a **resume score** with improvement tips  
✅ **Interactive dashboard** using Streamlit  
✅ Extended analytics with `enhanced_analytics.py`  

---

## **Installation & Setup**  

### **1️⃣ Clone the Repository**  
```bash
git clone https://github.com/yugvyas45/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer
```

### **2️⃣ Install Required Libraries**  
```bash
pip install -r requirements.txt
```

### **3️⃣ Set Up API Keys**  
-Get your Google Gemini AI API key.
-Create a .env file and add:
  ```
  GEMINI_API_KEY=your_api_key_here
  ```

### **4️⃣ Run the Application**  
```bash
streamlit run app.py
```

---

## **How It Works**  

1️⃣ **Upload a Resume (PDF Format)**  
2️⃣ **Paste a Job Description** into the text area  
3️⃣ Click **Analyze Resume**  
4️⃣ Get AI-generated insights, including:  
   - **Resume Score**  
   - **Matching Skills**  
   - **Unmatched Skills**  
   - **Improvement Suggestions**  

---

Project Structure
📂 AI-Resume-Analyzer  
 ┣ 📂 pdf_images/            # Temporary resume images  
 ┣ 📜 app.py                 # Main Streamlit app  
 ┣ 📜 analyzer.py            # Resume analysis logic  
 ┣ 📜 enhanced_analytics.py  # Extended analytics & improvements  
 ┣ 📜 requirements.txt       # Python dependencies  
 ┣ 📜 .gitignore             # Ignored files config  
 ┗ 📜 README.md              # Documentation  

Future Enhancements

🚀 Add batch resume analysis (multiple resumes at once)
🚀 Export results to PDF/Excel reports
🚀 Add ATS (Applicant Tracking System) compatibility check
🚀 Support multilingual resumes
🚀 Deploy to Streamlit Cloud / Hugging Face Spaces

--- 


Author

👤 Yug Vyas

🎓 Student at IIT Jodhpur (BS in AI & DS + B.Tech CSE)

💻 AI & Web Developer | ML Enthusiast

🌐 LinkedIn
 | GitHub

Acknowledgment

This project was inspired by Venkatesh0610's Resume Analyzer
.
I built upon the idea and added significant modifications, improvements, and custom analytics.

⭐ Don’t forget to star this repo if you find it helpful!

---

👉 Do you want me to also **generate a fresh `requirements.txt`** for you (based on your files `app.py`, `analyzer.py`, and `enhanced_analytics.py`), so anyone can install the dependencies in one go?

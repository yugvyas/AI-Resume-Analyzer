# import base64
# import os
# import logging
# from analyzer import pdf_to_jpg, process_image, extract_text_from_pdf, analyze_resume_enhanced  # Import image processing functions
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import fitz
# from PIL import Image
# import google.generativeai as genai
# import time

# # Configure logging
# logging.basicConfig(level=logging.INFO)

# # Set page layout to "wide"
# st.set_page_config(layout="wide")

# # Page Navigation State
# if "page" not in st.session_state:
#     st.session_state.page = "main"

# # Function to display project title
# def show_project_title():
#     st.markdown(
#         """
#         <h2 style="text-align: center; color: #4A90E2;">AI-Powered Resume Matcher</h2>
#         """,
#         unsafe_allow_html=True
#     )

# def show_loading_screen():
#     """Displays a full-screen loading spinner while processing."""
#     placeholder = st.empty()  # Create a placeholder for the spinner

#     with placeholder.container():
#         st.markdown(
#             """
#             <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%;
#                         background-color: rgba(0, 0, 0, 0.8); display: flex; justify-content: center;
#                         align-items: center; color: white; font-size: 24px; font-weight: bold; z-index: 999;">
#                 ⏳ Analyzing your resume... Please wait.
#             </div>
#             """,
#             unsafe_allow_html=True
#         )

#     return placeholder  # Return the placeholder so it can be removed later

# # Callback function to remove resume
# def remove_resume():
#     st.session_state.resume_uploaded = False
#     st.session_state.uploaded_file = None
#     if "file_path" in st.session_state:
#         # Clean up the saved file
#         try:
#             if os.path.exists(st.session_state.file_path):
#                 os.remove(st.session_state.file_path)
#         except Exception as e:
#             logging.warning(f"Could not remove file: {e}")
#         del st.session_state.file_path
#     if "extracted_data" in st.session_state:
#         del st.session_state.extracted_data
#     st.rerun()

# # Function to save uploaded file to root directory
# def save_uploaded_file(uploaded_file):
#     file_path = os.path.join(os.getcwd(), uploaded_file.name)  # Save in root directory
#     with open(file_path, "wb") as f:
#         f.write(uploaded_file.getbuffer())
#     return file_path  # Return file path

# # Function to display analytics page with extracted data
# def show_analytics():
#     show_project_title()  # Keep title on analytics page

#     st.title("📊 Resume & Job Description Analytics")

#     # Check if extracted data is available
#     if "extracted_data" in st.session_state and st.session_state.extracted_data:
#         extracted_data = st.session_state.extracted_data  # Retrieve JSON data

#         # Display Matching Score
#         overall_score = extracted_data.get("overall_score", 0)
#         st.subheader(f"Matching Score: {overall_score}%")

#         # **Gauge Chart for Score Visualization**
#         fig = px.bar(
#             x=[overall_score], y=["Resume Match"],
#             orientation="h", text=[f"{overall_score}%"],
#             color_discrete_sequence=[
#                 "#2ECC71" if overall_score >= 80 else "#F39C12" if overall_score >= 60 else "#E74C3C"]
#         )
#         fig.update_traces(textposition="inside")
#         fig.update_layout(xaxis=dict(range=[0, 100]), height=150, width=500)
#         st.plotly_chart(fig, use_container_width=True)

#         # Key Insights
#         st.subheader("🔍 Key Insights")
#         st.write(f"✅ Your resume matches **{overall_score}%** with the job description.")

#         if overall_score >= 80:
#             st.success("✅ Your resume **strongly aligns** with the job requirements! 🎯")
#         elif overall_score >= 60:
#             st.warning("⚠️ Your resume **partially aligns** with the job description. Consider improving a few areas.")
#         else:
#             st.error("🚨 Your resume needs **significant improvements** to match the job description.")

#         # **Top Matching Skills Section**
#         st.subheader("✅ Top Matching Skills")
#         matching_skills = extracted_data.get("keyword_matching", [])
#         if isinstance(matching_skills, list) and len(matching_skills) > 0:
#             top_matching = matching_skills[:5]
#             remaining_matching = matching_skills[5:]

#             if top_matching:
#                 st.success(", ".join(top_matching))  # Show top 5 matched skills
#             else:
#                 st.warning("No matching skills found.")

#             if remaining_matching:
#                 with st.expander(f"🔽 View all matched skills ({len(matching_skills)})"):
#                     st.write(", ".join(remaining_matching))
#         else:
#             st.warning("No matching skills found.")

#         # **Top Missing Skills Section**
#         st.subheader("⚠️ Top Missing Skills")
#         missing_skills = extracted_data.get("missing_keywords", [])
#         if isinstance(missing_skills, list) and len(missing_skills) > 0:
#             top_missing = missing_skills[:5]
#             remaining_missing = missing_skills[5:]

#             if top_missing:
#                 st.error(", ".join(top_missing))  # Show top 5 missing skills
#             else:
#                 st.success("Great! No critical missing skills.")

#             if remaining_missing:
#                 with st.expander(f"🔽 View all missing skills ({len(missing_skills)})"):
#                     st.write(", ".join(remaining_missing))
#         else:
#             st.success("Great! No critical missing skills.")

#         # **Categorized Improvements (Dynamic Sections)**
#         st.subheader("📌 Categorized Improvements")

#         suggestions = extracted_data.get("suggestions", [])

#         if isinstance(suggestions, list) and len(suggestions) > 0:
#             # **important_keys dynamically categorizes suggestions**
#             important_keys = {
#                 "Skills & Certifications": ["skill", "certification", "training"],
#                 "Experience & Work History": ["experience", "projects", "work history"],
#                 "Resume Formatting & Structure": ["format", "layout", "structure", "design"],
#                 "Education & Qualifications": ["education", "degree", "qualification"]
#             }

#             categorized_suggestions = {category: [] for category in important_keys.keys()}

#             # **Classify suggestions dynamically**
#             for suggestion in suggestions:
#                 categorized = False
#                 for category, keywords in important_keys.items():
#                     if any(word in suggestion.lower() for word in keywords):
#                         categorized_suggestions[category].append(f"🔹 {suggestion}")
#                         categorized = True
#                         break  # Stop checking further categories once assigned
                
#                 # If not categorized, add to general category
#                 if not categorized:
#                     if "General Improvements" not in categorized_suggestions:
#                         categorized_suggestions["General Improvements"] = []
#                     categorized_suggestions["General Improvements"].append(f"🔹 {suggestion}")

#             # **Display suggestions in expandable sections**
#             for category, items in categorized_suggestions.items():
#                 if items:  # Only show category if it has items
#                     with st.expander(f"📌 {category} ({len(items)})"):
#                         for item in items:
#                             st.markdown(item)

#             # **High-Priority Improvement Suggestions Table with Color Coding**
#             st.write("### 🚀 High-Priority Improvement Suggestions")

#             priority_data = []
#             for suggestion in suggestions:
#                 if "experience" in suggestion.lower():
#                     priority = "High"
#                     color = "🔴"  # Red for High Priority
#                 elif "skill" in suggestion.lower():
#                     priority = "Medium"
#                     color = "🟠"  # Orange for Medium Priority
#                 else:
#                     priority = "Low"
#                     color = "🟢"  # Green for Low Priority

#                 priority_data.append({
#                     "Improvement Suggestion": suggestion,
#                     "Priority": f"{color} {priority}"
#                 })

#             if priority_data:
#                 priority_df = pd.DataFrame(priority_data)
#                 priority_df = priority_df.sort_values(by="Priority", ascending=False).head(5)  # Show top 5 high-priority improvements

#                 # **Styled Table for Perfect UI Alignment**
#                 st.dataframe(priority_df, use_container_width=True)
#         else:
#             st.success("No major improvements needed. Well done!")

#     else:
#         st.error("No extracted data available. Please upload a resume first.")

#     # Add spacing and navigation button
#     st.markdown("<br>", unsafe_allow_html=True)
#     col_center = st.columns([1, 2, 1])[1]
#     with col_center:
#         if st.button("🔙 Back to Upload", use_container_width=True):
#             st.session_state.page = "main"
#             st.rerun()

# # Main Page: Job Description Input & Resume Upload
#     if st.session_state.page == "main":
#         show_project_title()  # Show title at the top

#         # Create two equal columns for Job Description & Resume Upload
#         col1, col2 = st.columns([1, 1], gap="medium")

#         # Left Column: Job Description Input
#         with col1:
#             st.subheader("Enter Job Description")
#             job_description = st.text_area("Paste the job description here", height=400, key="job_desc_input")

#         # Right Column: Resume Uploader & PDF Viewer
#         with col2:
#             if "resume_uploaded" not in st.session_state:
#                 st.session_state.resume_uploaded = False
#                 st.session_state.uploaded_file = None

#             if not st.session_state.resume_uploaded:
#                 st.subheader("Upload Resume")
#                 uploaded_file = st.file_uploader("Upload your PDF Resume", type=["pdf"], key="resume_uploader")

#                 if uploaded_file is not None:
#                     try:
#                         file_path = save_uploaded_file(uploaded_file)  # Save file to root dir
#                         st.session_state.resume_uploaded = True
#                         st.session_state.uploaded_file = uploaded_file
#                         st.session_state.file_path = file_path
#                         st.success("Resume uploaded successfully!")
#                         st.rerun()
#                     except Exception as e:
#                         st.error(f"Error uploading file: {str(e)}")

#             if st.session_state.resume_uploaded and st.session_state.uploaded_file:
#                 # Convert PDF to Base64 for preview
#                 def get_pdf_base64(file_path):
#                     try:
#                         with open(file_path, "rb") as file:
#                             base64_pdf = base64.b64encode(file.read()).decode("utf-8")
#                         return f"data:application/pdf;base64,{base64_pdf}"
#                     except Exception as e:
#                         st.error(f"Error displaying PDF: {str(e)}")
#                         return None

#                 pdf_data = get_pdf_base64(st.session_state.file_path)

#                 if pdf_data:
#                     # Display PDF with Close Button
#                     st.subheader("Uploaded Resume")

#                     # Add some vertical space before showing the PDF preview
#                     st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

#                     # Create two columns: PDF preview | Close button on the same row
#                     col3, col4 = st.columns([10, 1])
#                     with col3:
#                         st.markdown(
#                             f'<iframe src="{pdf_data}" width="100%" height="400" style="border: none; margin-top: 15px;"></iframe>',
#                             unsafe_allow_html=True,
#                         )
#                     with col4:
#                         if st.button("❌", key="remove_resume", help="Remove Resume", use_container_width=True):
#                             remove_resume()

#         # Check if both Job Description & Resume are uploaded
#         is_analyze_enabled = bool(job_description.strip()) and st.session_state.resume_uploaded

#         # Centered "Analyze Resume" Button Below Preview
#         st.markdown("<br>", unsafe_allow_html=True)  # Add space
#         col_center = st.columns([1, 2, 1])[1]  # Center column
#         with col_center:
#             if st.button("🔍 Analyze Resume", use_container_width=True, disabled=not is_analyze_enabled):
#                 if is_analyze_enabled:
#                     # Show progress steps
#                     progress_steps = [
#                         "Extracting text from PDF...",
#                         "Processing with AI...", 
#                         "Analyzing skills match...",
#                         "Generating suggestions...",
#                         "Creating visualizations..."
#                     ]
                    
#                     progress_bar = st.progress(0)
#                     status_text = st.empty()
                    
#                     try:
#                         # Step 1: Extract text directly (MUCH FASTER)
#                         status_text.text(progress_steps[0])
#                         progress_bar.progress(20)
                        
#                         text_data = extract_text_from_pdf(st.session_state.file_path)
                        
#                         if "error" in text_data:
#                             st.error(f"Error extracting text: {text_data['error']}")
#                             return
                        
#                         # Step 2-5: AI Analysis with progress updates
#                         for i, step in enumerate(progress_steps[1:], 2):
#                             status_text.text(step)
#                             progress_bar.progress(i * 20)
#                             time.sleep(0.3)  # Brief pause for UX
                        
#                         # Use enhanced analysis function
#                         result = analyze_resume_enhanced(job_description, text_data['full_text'])
                        
#                         if result and "error" not in result:
#                             st.session_state.extracted_data = result
#                             st.session_state.page = "analytics"
                            
#                             # Clear progress indicators
#                             progress_bar.empty()
#                             status_text.empty()
                            
#                             st.success("Analysis complete! Redirecting to results...")
#                             time.sleep(1)
#                             st.rerun()
#                         else:
#                             st.error(f"Analysis failed: {result.get('error', 'Unknown error') if result else 'Unknown error'}")
                            
#                     except Exception as e:
#                         st.error(f"Analysis failed: {str(e)}")
#                         logging.error(f"Analysis error: {str(e)}")
#                     finally:
#                         # Clean up progress indicators
#                         try:
#                             progress_bar.empty()
#                             status_text.empty()
#                         except:
#                             pass

#     # Show Analytics Page
#     elif st.session_state.page == "analytics":
#         show_analytics()













import base64
import os
import logging
import time
import streamlit as st
from analyzer import extract_text_from_pdf, analyze_resume_enhanced
from enhanced_analytics import show_enhanced_analytics

# Configure logging
logging.basicConfig(level=logging.INFO)

# Streamlit page settings
st.set_page_config(layout="wide", page_title="AI Resume Matcher")

# --- Utility functions ---
def show_project_title():
    st.markdown(
        "<h2 style='text-align: center; color: #4A90E2;'>AI-Powered Resume Matcher</h2>",
        unsafe_allow_html=True,
    )

def remove_resume():
    st.session_state.resume_uploaded = False
    st.session_state.uploaded_file = None
    if "file_path" in st.session_state and os.path.exists(st.session_state.file_path):
        try:
            os.remove(st.session_state.file_path)
        except Exception as e:
            logging.warning(f"Could not remove file: {e}")
        del st.session_state.file_path
    if "extracted_data" in st.session_state:
        del st.session_state.extracted_data
    # st.experimental_rerun()
    st.rerun()

def save_uploaded_file(uploaded_file):
    file_path = os.path.join(os.getcwd(), uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# --- Ensure page state is valid ---
page = st.session_state.get("page", "main")
if page not in ["main", "analytics"]:
    st.session_state.page = "main"
    page = "main"

# --- Main Page ---
if page == "main":
    show_project_title()
    col1, col2 = st.columns(2, gap="medium")

    # Left: Job description input
    with col1:
        st.subheader("Enter Job Description")
        job_description = st.text_area("Paste job description here", height=400, key="job_desc_input")

    # Right: Resume upload + preview
    with col2:
        if "resume_uploaded" not in st.session_state:
            st.session_state.resume_uploaded = False
            st.session_state.uploaded_file = None

        if not st.session_state.resume_uploaded:
            st.subheader("Upload Resume")
            uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], key="resume_uploader")

            if uploaded_file is not None:
                file_path = save_uploaded_file(uploaded_file)
                st.session_state.resume_uploaded = True
                st.session_state.uploaded_file = uploaded_file
                st.session_state.file_path = file_path
                st.success("Resume uploaded successfully!")
                st.rerun()

        if st.session_state.resume_uploaded and st.session_state.uploaded_file:
            st.subheader("Uploaded Resume")
            try:
                with open(st.session_state.file_path, "rb") as file:
                    base64_pdf = base64.b64encode(file.read()).decode("utf-8")
                st.markdown(
                    f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="400" style="border:none;"></iframe>',
                    unsafe_allow_html=True,
                )
            except Exception as e:
                st.error(f"Error displaying PDF: {str(e)}")

            if st.button("❌ Remove Resume", use_container_width=True):
                remove_resume()

    # Analyze button (enabled only if both fields filled)
    is_analyze_enabled = bool(job_description.strip()) and st.session_state.resume_uploaded
    st.markdown("<br>", unsafe_allow_html=True)
    center = st.columns([1, 2, 1])[1]
    with center:
        if st.button("🔍 Analyze Resume", use_container_width=True, disabled=not is_analyze_enabled):
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()
                steps = ["Extracting PDF text...", "Running AI analysis...", "Finalizing..."]

                for i, step in enumerate(steps, 1):
                    status_text.text(step)
                    progress_bar.progress(i * 30)
                    time.sleep(0.3)

                # Extract PDF text
                text_data = extract_text_from_pdf(st.session_state.file_path)
                if "error" in text_data:
                    st.error(f"Error extracting text: {text_data['error']}")
                else:
                    # Run AI analysis
                    result = analyze_resume_enhanced(job_description, text_data['full_text'])
                    if result and "error" not in result:
                        st.session_state.extracted_data = result
                        st.session_state.page = "analytics"
                        st.success("Analysis complete! Redirecting...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Analysis failed: {result.get('error','Unknown error') if result else 'Unknown error'}")
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                logging.error(f"Error: {str(e)}")
            finally:
                progress_bar.empty()
                status_text.empty()

elif page == "analytics":
    # Always show analytics if we have data, otherwise fallback
    if "extracted_data" in st.session_state and st.session_state.extracted_data:
        show_enhanced_analytics()
    else:
        st.warning("No analysis data found. Returning to main page.")
        st.session_state.page = "main"
        st.rerun()

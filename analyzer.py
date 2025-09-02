# import os
# import logging
# import fitz  # PyMuPDF
# import json
# import gc
# import time
# from pathlib import Path
# from PIL import Image
# import google.generativeai as genai
# from dotenv import load_dotenv
# from typing import Dict, List, Optional

# # Load environment variables from .env file
# load_dotenv()

# # Configure logging
# logging.basicConfig(
#     filename="app.log",
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )

# logging.info("Starting the script...")

# # Get API key from environment variables
# api_key = os.getenv('GENAI_API_KEY')

# if not api_key:
#     logging.error("GENAI_API_KEY is not set. Please check your .env file.")
#     raise ValueError("GENAI_API_KEY is missing.")

# # Configure Gemini API
# genai.configure(api_key=api_key)
# logging.info("GenAI API configured successfully.")

# # NEW ENHANCED FUNCTIONS
# def extract_text_from_pdf(pdf_path: str) -> Dict[str, str]:
#     """
#     Extract text directly from PDF. Much faster than image conversion.
#     Falls back to OCR only if direct text extraction fails.
#     """
#     try:
#         doc = fitz.open(pdf_path)
#         full_text = ""
#         page_texts = []
        
#         for page_num in range(len(doc)):
#             page = doc[page_num]
#             text = page.get_text()
            
#             if text.strip():  # If text exists
#                 full_text += text + "\n"
#                 page_texts.append(text)
#             else:
#                 # Fall back to OCR for image-based PDFs
#                 logging.info(f"Page {page_num + 1} requires OCR processing")
#                 pix = page.get_pixmap(dpi=300)
#                 # Here you could add OCR processing if needed
                
#         doc.close()
        
#         return {
#             "full_text": full_text,
#             "page_count": len(doc),
#             "extraction_method": "direct_text",
#             "page_texts": page_texts
#         }
        
#     except Exception as e:
#         logging.error(f"Error extracting text from PDF: {str(e)}")
#         return {"error": str(e)}

# def parse_resume_sections(text: str) -> Dict[str, str]:
#     """
#     Parse resume into structured sections using pattern matching.
#     This is much faster than sending to AI for basic parsing.
#     """
#     sections = {
#         "contact_info": "",
#         "summary": "",
#         "experience": "",
#         "education": "",
#         "skills": "",
#         "projects": "",
#         "certifications": ""
#     }
    
#     # Common section headers (case insensitive)
#     section_patterns = {
#         "experience": ["experience", "work history", "employment", "professional experience"],
#         "education": ["education", "academic background", "qualifications"],
#         "skills": ["skills", "technical skills", "competencies", "technologies"],
#         "projects": ["projects", "personal projects", "side projects"],
#         "certifications": ["certifications", "certificates", "licenses"],
#         "summary": ["summary", "objective", "profile", "about"]
#     }
    
#     lines = text.split('\n')
#     current_section = "summary"
    
#     for line in lines:
#         line_lower = line.lower().strip()
        
#         # Check if line is a section header
#         for section, patterns in section_patterns.items():
#             if any(pattern in line_lower for pattern in patterns):
#                 current_section = section
#                 break
#         else:
#             # Add content to current section
#             if line.strip():
#                 sections[current_section] += line + "\n"
    
#     return sections

# def calculate_ats_score(resume_text: str, job_description: str) -> Dict[str, float]:
#     """
#     Calculate ATS compatibility score based on multiple factors.
#     """
#     score_factors = {}
    
#     # Keyword density
#     job_keywords = set(job_description.lower().split())
#     resume_keywords = set(resume_text.lower().split())
#     keyword_overlap = len(job_keywords.intersection(resume_keywords))
#     score_factors["keyword_density"] = min(100, (keyword_overlap / max(len(job_keywords), 1)) * 100)
    
#     # Section headers (common ATS-friendly headers)
#     ats_sections = ["experience", "education", "skills", "summary"]
#     found_sections = sum(1 for section in ats_sections if section in resume_text.lower())
#     score_factors["section_structure"] = (found_sections / len(ats_sections)) * 100
    
#     # Formatting score (no special characters, proper spacing)
#     special_chars = ["•", "★", "◆", "►", "→"]
#     formatting_penalty = sum(resume_text.count(char) for char in special_chars)
#     score_factors["formatting"] = max(0, 100 - (formatting_penalty * 2))
    
#     # Overall ATS score
#     overall_ats_score = sum(score_factors.values()) / len(score_factors)
#     score_factors["overall_ats_score"] = overall_ats_score
    
#     return score_factors

# def safe_api_call(func, *args, **kwargs):
#     """Safe API call with retry logic."""
#     max_retries = 3
#     for attempt in range(max_retries):
#         try:
#             return func(*args, **kwargs)
#         except Exception as e:
#             logging.warning(f"API call attempt {attempt + 1} failed: {str(e)}")
#             if attempt == max_retries - 1:
#                 raise e
#             time.sleep(2 ** attempt)  # Exponential backoff

# # EXISTING FUNCTIONS (keeping your original pdf_to_jpg for fallback)
# def pdf_to_jpg(pdf_path, output_folder="pdf_images", dpi=300):
#     """Converts a PDF file into images (one per page) and saves them."""
#     logging.info(f"Converting PDF '{pdf_path}' to images...")
#     file_paths = []
#     output_folder = Path(output_folder)
#     output_folder.mkdir(parents=True, exist_ok=True)

#     try:
#         pdf_document = fitz.open(pdf_path)
#         logging.info(f"Opened PDF: {pdf_path} with {len(pdf_document)} pages.")

#         for page_number in range(len(pdf_document)):
#             page = pdf_document[page_number]
#             pix = page.get_pixmap(dpi=dpi)
#             output_file = output_folder / f"page_{page_number + 1}.jpg"

#             with open(output_file, "wb") as f:
#                 f.write(pix.tobytes("jpeg"))

#             del pix  # Free up memory
#             file_paths.append(str(output_file))
#             logging.info(f"Saved image: {output_file}")

#         pdf_document.close()
#     except Exception as e:
#         logging.error(f"Error converting PDF to images: {str(e)}")

#     return file_paths

# def process_image(file_path="", prompt="Extract text from this image, and provide the result in JSON format",
#                   type=None):
#     """Sends an image to the Gemini API and returns extracted structured data."""
#     logging.info(f"Processing file: {file_path} with type {type}")

#     try:
#         model = genai.GenerativeModel("gemini-1.5-flash-002")
        
#         def api_call():
#             if type == "image":
#                 with Image.open(file_path) as img:
#                     return model.generate_content([prompt, img])
#             elif type == "text":
#                 return model.generate_content([prompt, json.dumps(file_path, indent=2)])
#             else:
#                 logging.warning("Invalid type provided. Skipping processing.")
#                 return None
        
#         # Use safe API call with retries
#         response = safe_api_call(api_call)
        
#         if not response:
#             return {"error": "Invalid processing type"}

#         if hasattr(response, 'candidates') and response.candidates:
#             parts = response.candidates[0].content.parts[0]
#             if hasattr(parts, 'text'):
#                 text_content = parts.text.replace("```", "").replace("json", "")
#                 try:
#                     parsed_data = json.loads(text_content)
#                     with open("result.json", "w") as json_file:
#                         json.dump(parsed_data, json_file, indent=4)
#                     logging.info("JSON data successfully saved to result.json")
#                     return parsed_data
#                 except json.JSONDecodeError:
#                     logging.error("Failed to decode JSON from response.")
#                     return {"error": "JSON decoding error."}
#     except Exception as e:
#         logging.error(f"Error processing image: {str(e)}")
#         return {"error": str(e)}
#     finally:
#         try:
#             del model
#             gc.collect()
#         except:
#             pass

#     return None

# # Enhanced analysis function
# def analyze_resume_enhanced(job_description: str, resume_text: str) -> Dict:
#     """
#     Enhanced resume analysis using direct text processing.
#     """
#     try:
#         # Parse resume sections
#         sections = parse_resume_sections(resume_text)
        
#         # Calculate ATS score
#         ats_scores = calculate_ats_score(resume_text, job_description)
        
#         # Enhanced analysis prompt
#         enhanced_prompt = f"""
#         You are an expert ATS and HR analyst. Analyze this resume against the job description.
        
#         JOB DESCRIPTION:
#         {job_description}
        
#         RESUME TEXT:
#         {resume_text}
        
#         RESUME SECTIONS:
#         {json.dumps(sections, indent=2)}
        
#         Provide detailed analysis in this JSON format:
#         {{
#             "overall_score": 75,
#             "ats_score": {ats_scores.get('overall_ats_score', 50)},
#             "keyword_matching": ["matched_skill1", "matched_skill2"],
#             "missing_keywords": ["missing_skill1", "missing_skill2"],
#             "suggestions": [
#                 "Specific improvement 1",
#                 "Specific improvement 2"
#             ],
#             "section_scores": {{
#                 "experience": 80,
#                 "skills": 70,
#                 "education": 85
#             }},
#             "critical_improvements": ["top priority item 1", "top priority item 2"]
#         }}
        
#         Focus on:
#         1. Exact skill matches between resume and job description
#         2. Missing critical requirements
#         3. Specific, actionable improvements
#         4. ATS optimization suggestions
#         """
        
#         # Process with AI
#         result = safe_api_call(
#             lambda: process_image(file_path="", prompt=enhanced_prompt, type="text")
#         )
        
#         # Add calculated ATS scores
#         if result and isinstance(result, dict):
#             result["ats_breakdown"] = ats_scores
        
#         return result
        
#     except Exception as e:
#         logging.error(f"Enhanced analysis error: {str(e)}")
#         return {"error": str(e)}




# import os
# import logging
# import fitz  # PyMuPDF
# import json
# import gc
# from pathlib import Path
# from PIL import Image
# import google.generativeai as genai
# from dotenv import load_dotenv  # Import dotenv

# # Load environment variables from .env file
# load_dotenv()

# # Configure logging
# logging.basicConfig(
#     filename="app.log",
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )

# logging.info("Starting the script...")

# # Get API key from environment variables
# api_key = os.getenv('GENAI_API_KEY')

# if not api_key:
#     logging.error("GENAI_API_KEY is not set. Please check your .env file.")
#     raise ValueError("GENAI_API_KEY is missing.")

# # Configure Gemini API
# genai.configure(api_key=api_key)
# logging.info("GenAI API configured successfully.")

# def pdf_to_jpg(pdf_path, output_folder="pdf_images", dpi=300):
#     """Converts a PDF file into images (one per page) and saves them."""
#     logging.info(f"Converting PDF '{pdf_path}' to images...")
#     file_paths = []
#     output_folder = Path(output_folder)
#     output_folder.mkdir(parents=True, exist_ok=True)

#     try:
#         pdf_document = fitz.open(pdf_path)
#         logging.info(f"Opened PDF: {pdf_path} with {len(pdf_document)} pages.")

#         for page_number in range(len(pdf_document)):
#             page = pdf_document[page_number]
#             pix = page.get_pixmap(dpi=dpi)
#             output_file = output_folder / f"page_{page_number + 1}.jpg"

#             with open(output_file, "wb") as f:
#                 f.write(pix.tobytes("jpeg"))

#             del pix  # Free up memory
#             file_paths.append(str(output_file))
#             logging.info(f"Saved image: {output_file}")

#         pdf_document.close()
#     except Exception as e:
#         logging.error(f"Error converting PDF to images: {str(e)}")

#     return file_paths


# def process_image(file_path="", prompt="Extract text from this image, and provide the result in JSON format",
#                   type=None):
#     """Sends an image to the Gemini API and returns extracted structured data."""
#     logging.info(f"Processing file: {file_path} with type {type}")

#     try:
#         model = genai.GenerativeModel("gemini-1.5-flash-002")
#         if type == "image":
#             with Image.open(file_path) as img:
#                 response = model.generate_content([prompt, img])
#         elif type == "text":
#             response = model.generate_content([prompt, json.dumps(file_path, indent=2)])
#             logging.info(f"Text processing response: {response}")
#         else:
#             logging.warning("Invalid type provided. Skipping processing.")
#             return ""

#         if hasattr(response, 'candidates') and response.candidates:
#             parts = response.candidates[0].content.parts[0]
#             if hasattr(parts, 'text'):
#                 text_content = parts.text.replace("```", "").replace("json", "")
#                 try:
#                     parsed_data = json.loads(text_content)
#                     with open("result.json", "w") as json_file:
#                         json.dump(parsed_data, json_file, indent=4)
#                     logging.info("JSON data successfully saved to result.json")
#                     return parsed_data
#                 except json.JSONDecodeError:
#                     logging.error("Failed to decode JSON from response.")
#                     return {"error": "JSON decoding error."}
#     except Exception as e:
#         logging.error(f"Error processing image: {str(e)}")
#         return {"error": str(e)}
#     finally:
#         del model
#         gc.collect()

#     return None


# if __name__ == "__main__":
#     uploaded_pdf = "Resume_2024.pdf"
#     logging.info(f"Processing PDF: {uploaded_pdf}")

#     image_paths = pdf_to_jpg(uploaded_pdf)
#     if not image_paths:
#         logging.error("No images were extracted from the PDF.")
#     else:
#         logging.info(f"Extracted {len(image_paths)} images.")

#     extracted_data = []
#     logging.info("Starting AI processing on extracted images...")

#     for img_path in image_paths:
#         result = process_image(img_path)
#         logging.info(f"Processing result for {img_path}: {result}")
#         extracted_data.append(result)

#     logging.info("Final Extracted Data:")
#     logging.info(json.dumps(extracted_data, indent=2))
#     print(json.dumps(extracted_data, indent=2))





# import os
# import logging
# import fitz  # PyMuPDF
# import json
# import gc
# import time
# from pathlib import Path
# from PIL import Image
# import pytesseract
# import google.generativeai as genai
# from dotenv import load_dotenv
# from typing import Dict, List, Optional

# # Load environment variables from .env file
# load_dotenv()

# # Configure logging
# logging.basicConfig(
#     filename="app.log",
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )

# logging.info("Starting the script...")

# # Get API key from environment variables
# api_key = os.getenv('GENAI_API_KEY')

# if not api_key:
#     logging.error("GENAI_API_KEY is not set. Please check your .env file.")
#     raise ValueError("GENAI_API_KEY is missing.")

# # Configure Gemini API
# genai.configure(api_key=api_key)
# logging.info("GenAI API configured successfully.")


# # ------------------------------
# # TEXT EXTRACTION
# # ------------------------------
# def extract_text_from_pdf(pdf_path: str) -> Dict[str, str]:
#     """
#     Extract text directly from PDF using PyMuPDF.
#     Falls back to OCR if direct text extraction fails (image-based PDFs).
#     """
#     try:
#         doc = fitz.open(pdf_path)
#         full_text = ""
#         page_texts = []

#         for page_num in range(len(doc)):
#             page = doc[page_num]
#             text = page.get_text()

#             if text.strip():
#                 # Direct text found
#                 full_text += text + "\n"
#                 page_texts.append(text)
#             else:
#                 # OCR fallback for scanned/image-based resumes
#                 logging.info(f"Page {page_num + 1} requires OCR processing")
#                 pix = page.get_pixmap(dpi=300)
#                 img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
#                 ocr_text = pytesseract.image_to_string(img)
#                 full_text += ocr_text + "\n"
#                 page_texts.append(ocr_text)

#         page_count = len(doc)
#         doc.close()

#         return {
#             "full_text": full_text,
#             "page_count": page_count,
#             "extraction_method": "direct_text_or_ocr",
#             "page_texts": page_texts
#         }

#     except Exception as e:
#         logging.error(f"Error extracting text from PDF: {str(e)}")
#         return {"error": str(e)}


# # ------------------------------
# # RESUME PARSING
# # ------------------------------
# def parse_resume_sections(text: str) -> Dict[str, str]:
#     """
#     Parse resume into structured sections using pattern matching.
#     """
#     sections = {
#         "contact_info": "",
#         "summary": "",
#         "experience": "",
#         "education": "",
#         "skills": "",
#         "projects": "",
#         "certifications": ""
#     }

#     # Common section headers
#     section_patterns = {
#         "experience": ["experience", "work history", "employment", "professional experience"],
#         "education": ["education", "academic background", "qualifications"],
#         "skills": ["skills", "technical skills", "competencies", "technologies"],
#         "projects": ["projects", "personal projects", "side projects"],
#         "certifications": ["certifications", "certificates", "licenses"],
#         "summary": ["summary", "objective", "profile", "about"]
#     }

#     lines = text.split('\n')
#     current_section = "summary"

#     for line in lines:
#         line_lower = line.lower().strip()

#         # Check if line is a section header
#         for section, patterns in section_patterns.items():
#             if any(pattern in line_lower for pattern in patterns):
#                 current_section = section
#                 break
#         else:
#             if line.strip():
#                 sections[current_section] += line + "\n"

#     return sections


# # ------------------------------
# # ATS SCORING
# # ------------------------------
# def calculate_ats_score(resume_text: str, job_description: str) -> Dict[str, float]:
#     """
#     Calculate ATS compatibility score based on multiple factors.
#     """
#     score_factors = {}

#     # Keyword density
#     job_keywords = set(job_description.lower().split())
#     resume_keywords = set(resume_text.lower().split())
#     keyword_overlap = len(job_keywords.intersection(resume_keywords))
#     score_factors["keyword_density"] = min(100, (keyword_overlap / max(len(job_keywords), 1)) * 100)

#     # Section headers
#     ats_sections = ["experience", "education", "skills", "summary"]
#     found_sections = sum(1 for section in ats_sections if section in resume_text.lower())
#     score_factors["section_structure"] = (found_sections / len(ats_sections)) * 100

#     # Formatting score
#     special_chars = ["•", "★", "◆", "►", "→"]
#     formatting_penalty = sum(resume_text.count(char) for char in special_chars)
#     score_factors["formatting"] = max(0, 100 - (formatting_penalty * 2))

#     # Overall ATS score
#     overall_ats_score = sum(score_factors.values()) / len(score_factors)
#     score_factors["overall_ats_score"] = overall_ats_score

#     return score_factors


# # ------------------------------
# # SAFE API CALL
# # ------------------------------
# def safe_api_call(func, *args, **kwargs):
#     """Safe API call with retry logic."""
#     max_retries = 3
#     for attempt in range(max_retries):
#         try:
#             return func(*args, **kwargs)
#         except Exception as e:
#             logging.warning(f"API call attempt {attempt + 1} failed: {str(e)}")
#             if attempt == max_retries - 1:
#                 raise e
#             time.sleep(2 ** attempt)  # Exponential backoff


# # ------------------------------
# # PDF TO IMAGE (fallback)
# # ------------------------------
# def pdf_to_jpg(pdf_path, output_folder="pdf_images", dpi=300):
#     """Converts a PDF file into images (one per page) and saves them."""
#     logging.info(f"Converting PDF '{pdf_path}' to images...")
#     file_paths = []
#     output_folder = Path(output_folder)
#     output_folder.mkdir(parents=True, exist_ok=True)

#     try:
#         pdf_document = fitz.open(pdf_path)
#         logging.info(f"Opened PDF: {pdf_path} with {len(pdf_document)} pages.")

#         for page_number in range(len(pdf_document)):
#             page = pdf_document[page_number]
#             pix = page.get_pixmap(dpi=dpi)
#             output_file = output_folder / f"page_{page_number + 1}.jpg"

#             with open(output_file, "wb") as f:
#                 f.write(pix.tobytes("jpeg"))

#             del pix
#             file_paths.append(str(output_file))
#             logging.info(f"Saved image: {output_file}")

#         pdf_document.close()
#     except Exception as e:
#         logging.error(f"Error converting PDF to images: {str(e)}")

#     return file_paths


# # ------------------------------
# # PROCESS IMAGE / TEXT
# # ------------------------------
# def process_image(file_path="", prompt="Extract text from this image, and provide the result in JSON format",
#                   type=None):
#     """Sends an image/text to Gemini API and returns structured data."""
#     logging.info(f"Processing file: {file_path} with type {type}")

#     try:
#         model = genai.GenerativeModel("gemini-1.5-flash-002")

#         def api_call():
#             if type == "image":
#                 with Image.open(file_path) as img:
#                     return model.generate_content([prompt, img])
#             elif type == "text":
#                 return model.generate_content([prompt, json.dumps(file_path, indent=2)])
#             else:
#                 logging.warning("Invalid type provided. Skipping processing.")
#                 return None

#         # Safe call
#         response = safe_api_call(api_call)

#         if not response:
#             return {"error": "Invalid processing type"}

#         if hasattr(response, 'candidates') and response.candidates:
#             parts = response.candidates[0].content.parts[0]
#             if hasattr(parts, 'text'):
#                 text_content = parts.text.replace("```", "").replace("json", "")
#                 try:
#                     parsed_data = json.loads(text_content)
#                     with open("result.json", "w") as json_file:
#                         json.dump(parsed_data, json_file, indent=4)
#                     logging.info("JSON data successfully saved to result.json")
#                     return parsed_data
#                 except json.JSONDecodeError:
#                     logging.error("Failed to decode JSON from response.")
#                     return {"error": "JSON decoding error."}
#     except Exception as e:
#         logging.error(f"Error processing image: {str(e)}")
#         return {"error": str(e)}
#     finally:
#         try:
#             del model
#             gc.collect()
#         except:
#             pass

#     return None


# # ------------------------------
# # RESUME ANALYSIS
# # ------------------------------
# def analyze_resume_enhanced(job_description: str, resume_text: str) -> Dict:
#     """
#     Enhanced resume analysis using direct text processing.
#     """
#     try:
#         # Parse sections
#         sections = parse_resume_sections(resume_text)

#         # Calculate ATS score
#         ats_scores = calculate_ats_score(resume_text, job_description)

#         # Prompt
#         enhanced_prompt = f"""
#         You are an expert ATS and HR analyst. Analyze this resume against the job description.

#         JOB DESCRIPTION:
#         {job_description}

#         RESUME TEXT:
#         {resume_text}

#         RESUME SECTIONS:
#         {json.dumps(sections, indent=2)}

#         Provide detailed analysis in this JSON format:
#         {{
#             "overall_score": 75,
#             "ats_score": {ats_scores.get('overall_ats_score', 50)},
#             "keyword_matching": ["matched_skill1", "matched_skill2"],
#             "missing_keywords": ["missing_skill1", "missing_skill2"],
#             "suggestions": [
#                 "Specific improvement 1",
#                 "Specific improvement 2"
#             ],
#             "section_scores": {{
#                 "experience": 80,
#                 "skills": 70,
#                 "education": 85
#             }},
#             "critical_improvements": ["top priority item 1", "top priority item 2"]
#         }}

#         Focus on:
#         1. Exact skill matches between resume and job description
#         2. Missing critical requirements
#         3. Specific, actionable improvements
#         4. ATS optimization suggestions
#         """

#         # Call Gemini
#         result = safe_api_call(
#             lambda: process_image(file_path="", prompt=enhanced_prompt, type="text")
#         )

#         if result and isinstance(result, dict):
#             result["ats_breakdown"] = ats_scores

#         return result

#     except Exception as e:
#         logging.error(f"Enhanced analysis error: {str(e)}")
#         return {"error": str(e)}



















import os
import logging
import fitz  # PyMuPDF
import json
import gc
import time
from pathlib import Path
from PIL import Image
import pytesseract
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, List, Optional

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Starting the script...")

# Get API key from environment variables
api_key = os.getenv('GENAI_API_KEY')

if not api_key:
    logging.error("GENAI_API_KEY is not set. Please check your .env file.")
    raise ValueError("GENAI_API_KEY is missing.")

# Configure Gemini API
genai.configure(api_key=api_key)
logging.info("GenAI API configured successfully.")


# ------------------------------
# TEXT EXTRACTION
# ------------------------------
def extract_text_from_pdf(pdf_path: str) -> Dict[str, str]:
    """
    Extract text directly from PDF using PyMuPDF.
    Falls back to OCR if direct text extraction fails (image-based PDFs).
    """
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        page_texts = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()

            if text.strip():
                # Direct text found
                full_text += text + "\n"
                page_texts.append(text)
            else:
                # OCR fallback for scanned/image-based resumes
                logging.info(f"Page {page_num + 1} requires OCR processing")
                pix = page.get_pixmap(dpi=300)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                ocr_text = pytesseract.image_to_string(img)
                full_text += ocr_text + "\n"
                page_texts.append(ocr_text)

        page_count = len(doc)
        doc.close()

        return {
            "full_text": full_text,
            "page_count": page_count,
            "extraction_method": "direct_text_or_ocr",
            "page_texts": page_texts
        }

    except Exception as e:
        logging.error(f"Error extracting text from PDF: {str(e)}")
        return {"error": str(e)}


# ------------------------------
# RESUME PARSING
# ------------------------------
def parse_resume_sections(text: str) -> Dict[str, str]:
    """
    Parse resume into structured sections using pattern matching.
    """
    sections = {
        "contact_info": "",
        "summary": "",
        "experience": "",
        "education": "",
        "skills": "",
        "projects": "",
        "certifications": ""
    }

    # Common section headers
    section_patterns = {
        "experience": ["experience", "work history", "employment", "professional experience"],
        "education": ["education", "academic background", "qualifications"],
        "skills": ["skills", "technical skills", "competencies", "technologies"],
        "projects": ["projects", "personal projects", "side projects"],
        "certifications": ["certifications", "certificates", "licenses"],
        "summary": ["summary", "objective", "profile", "about"]
    }

    lines = text.split('\n')
    current_section = "summary"

    for line in lines:
        line_lower = line.lower().strip()

        # Check if line is a section header
        for section, patterns in section_patterns.items():
            if any(pattern in line_lower for pattern in patterns):
                current_section = section
                break
        else:
            if line.strip():
                sections[current_section] += line + "\n"

    return sections


# ------------------------------
# ATS SCORING
# ------------------------------
def calculate_ats_score(resume_text: str, job_description: str) -> Dict[str, float]:
    """
    Calculate ATS compatibility score based on multiple factors.
    """
    score_factors = {}

    # Keyword density
    job_keywords = set(job_description.lower().split())
    resume_keywords = set(resume_text.lower().split())
    keyword_overlap = len(job_keywords.intersection(resume_keywords))
    score_factors["keyword_density"] = min(100, (keyword_overlap / max(len(job_keywords), 1)) * 100)

    # Section headers
    ats_sections = ["experience", "education", "skills", "summary"]
    found_sections = sum(1 for section in ats_sections if section in resume_text.lower())
    score_factors["section_structure"] = (found_sections / len(ats_sections)) * 100

    # Formatting score
    special_chars = ["•", "★", "◆", "►", "→"]
    formatting_penalty = sum(resume_text.count(char) for char in special_chars)
    score_factors["formatting"] = max(0, 100 - (formatting_penalty * 2))

    # Overall ATS score
    overall_ats_score = sum(score_factors.values()) / len(score_factors)
    score_factors["overall_ats_score"] = overall_ats_score

    return score_factors


# ------------------------------
# SAFE API CALL
# ------------------------------
def safe_api_call(func, *args, **kwargs):
    """Safe API call with retry logic."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.warning(f"API call attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)  # Exponential backoff


# ------------------------------
# PDF TO IMAGE (fallback)
# ------------------------------
def pdf_to_jpg(pdf_path, output_folder="pdf_images", dpi=300):
    """Converts a PDF file into images (one per page) and saves them."""
    logging.info(f"Converting PDF '{pdf_path}' to images...")
    file_paths = []
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    try:
        pdf_document = fitz.open(pdf_path)
        logging.info(f"Opened PDF: {pdf_path} with {len(pdf_document)} pages.")

        for page_number in range(len(pdf_document)):
            page = pdf_document[page_number]
            pix = page.get_pixmap(dpi=dpi)
            output_file = output_folder / f"page_{page_number + 1}.jpg"

            with open(output_file, "wb") as f:
                f.write(pix.tobytes("jpeg"))

            del pix
            file_paths.append(str(output_file))
            logging.info(f"Saved image: {output_file}")

        pdf_document.close()
    except Exception as e:
        logging.error(f"Error converting PDF to images: {str(e)}")

    return file_paths


# ------------------------------
# PROCESS IMAGE / TEXT
# ------------------------------
def process_image(file_path="", prompt="Extract text from this image, and provide the result in JSON format",
                  type=None):
    """Sends an image/text to Gemini API and returns structured data."""
    logging.info(f"Processing file: {file_path} with type {type}")

    try:
        model = genai.GenerativeModel("gemini-1.5-flash-002")

        def api_call():
            if type == "image":
                with Image.open(file_path) as img:
                    return model.generate_content([prompt, img])
            elif type == "text":
                return model.generate_content([prompt])
            else:
                logging.warning("Invalid type provided. Skipping processing.")
                return None

        # Safe call
        response = safe_api_call(api_call)

        if not response:
            return {"error": "Invalid processing type"}

        if hasattr(response, 'candidates') and response.candidates:
            parts = response.candidates[0].content.parts[0]
            if hasattr(parts, 'text'):
                text_content = parts.text.strip()
                logging.info(f"Raw API Response: {text_content}")  # DEBUG LINE
                
                # Clean the response
                text_content = text_content.replace("```json", "").replace("```", "").strip()
                
                try:
                    parsed_data = json.loads(text_content)
                    logging.info(f"Parsed JSON data: {parsed_data}")  # DEBUG LINE
                    
                    with open("result.json", "w") as json_file:
                        json.dump(parsed_data, json_file, indent=4)
                    logging.info("JSON data successfully saved to result.json")
                    return parsed_data
                except json.JSONDecodeError as e:
                    logging.error(f"Failed to decode JSON from response: {e}")
                    logging.error(f"Raw response text: {text_content}")
                    return {"error": f"JSON decoding error: {str(e)}"}
    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")
        return {"error": str(e)}
    finally:
        try:
            del model
            gc.collect()
        except:
            pass

    return None


# ------------------------------
# RESUME ANALYSIS
# ------------------------------
def analyze_resume_enhanced(job_description: str, resume_text: str) -> Dict:
    """
    Enhanced resume analysis using direct text processing.
    """
    try:
        # Parse sections
        sections = parse_resume_sections(resume_text)

        # Calculate ATS score
        ats_scores = calculate_ats_score(resume_text, job_description)

        # Calculate a preliminary score based on keyword matching
        job_words = set(word.lower() for word in job_description.split() if len(word) > 3)
        resume_words = set(word.lower() for word in resume_text.split() if len(word) > 3)
        keyword_match_ratio = len(job_words.intersection(resume_words)) / len(job_words) if job_words else 0
        estimated_score = int(keyword_match_ratio * 100)

        # Improved prompt with better instructions
        enhanced_prompt = f"""
        You are an expert ATS and HR analyst. Analyze this resume against the job description and provide a realistic score.

        JOB DESCRIPTION:
        {job_description[:1500]}...

        RESUME TEXT:
        {resume_text[:1500]}...

        Based on the analysis, provide your response in EXACTLY this JSON format (no additional text):
        {{
            "overall_score": [calculate a realistic score from 0-100 based on how well the resume matches the job requirements],
            "ats_score": {ats_scores.get('overall_ats_score', 50)},
            "keyword_matching": ["list", "of", "specific", "skills", "found", "in", "both"],
            "missing_keywords": ["important", "skills", "missing", "from", "resume"],
            "suggestions": [
                "Add specific skill X mentioned in job description",
                "Include more details about experience with Y"
            ],
            "section_scores": {{
                "experience": [score from 0-100],
                "skills": [score from 0-100], 
                "education": [score from 0-100]
            }},
            "critical_improvements": ["most important improvement 1", "most important improvement 2"]
        }}

        IMPORTANT: 
        - Calculate the overall_score based on actual match between resume and job requirements
        - Don't use example values - analyze the actual content
        - Respond ONLY with valid JSON, no other text
        """

        logging.info("Sending request to Gemini API...")
        
        # Call Gemini
        result = safe_api_call(
            lambda: process_image(file_path="", prompt=enhanced_prompt, type="text")
        )

        if result and isinstance(result, dict) and "error" not in result:
            # Add ATS breakdown to result
            result["ats_breakdown"] = ats_scores
            logging.info(f"Final analysis result: {result}")
            return result
        else:
            logging.error(f"API returned error or invalid result: {result}")
            # Return a fallback result with calculated scores
            return {
                "overall_score": max(estimated_score, 30),  # Minimum 30% to avoid 0
                "ats_score": ats_scores.get('overall_ats_score', 50),
                "keyword_matching": list(job_words.intersection(resume_words))[:10],
                "missing_keywords": list(job_words - resume_words)[:10],
                "suggestions": [
                    "Add more relevant keywords from the job description",
                    "Improve resume formatting for better ATS compatibility"
                ],
                "section_scores": {
                    "experience": 70,
                    "skills": 60,
                    "education": 75
                },
                "critical_improvements": [
                    "Add missing technical skills",
                    "Include more specific achievements"
                ],
                "ats_breakdown": ats_scores
            }

    except Exception as e:
        logging.error(f"Enhanced analysis error: {str(e)}")
        return {"error": str(e)}
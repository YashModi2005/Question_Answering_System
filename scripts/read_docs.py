from docx import Document
import os

def read_docx(file_path):
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return
    try:
        doc = Document(file_path)
        print(f"--- Content of {file_path} ---")
        for para in doc.paragraphs:
            if para.text.strip():
                print(para.text)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

read_docx("coverPage_Capstone Project.docx")
read_docx("CAPSTONE PROJECT PROPOSAL FORMAT.docx")

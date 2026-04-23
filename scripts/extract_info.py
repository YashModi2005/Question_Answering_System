from docx import Document
import os

def extract_info():
    file_path = "coverPage_Capstone Project.docx"
    if not os.path.exists(file_path):
        return
    
    doc = Document(file_path)
    content = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            content.append(text)
    
    print("\n".join(content))

if __name__ == "__main__":
    extract_info()

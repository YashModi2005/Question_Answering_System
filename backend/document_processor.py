import pdfplumber
import io
import re

class DocumentProcessor:
    def __init__(self, chunk_size=1000, chunk_overlap=150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_text_from_pdf(self, file_content):
        """Extracts text from a PDF file stream using pdfplumber for better table handling."""
        text = ""
        try:
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                for page in pdf.pages:
                    # extract_text(layout=True) can sometimes help with table structures
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error during PDF extraction with pdfplumber: {e}")
            # Fallback to a simple message if extraction fails completely
            return ""
        
        # Basic cleaning: Preserve single newlines but collapse multiple ones
        # This helps maintain some of the original structure (like table rows)
        text = re.sub(r'\n{3,}', '\n\n', text).strip()
        return text

    def chunk_text(self, text):
        """Splits text into smaller chunks with overlap."""
        if not text:
            return []
            
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + self.chunk_size
            
            # If not at the end, try to find a space or newline to avoid cutting words
            if end < text_len:
                # Look for the last newline or space within the last 50 characters of the chunk
                # Newlines are better for preserving table/list boundaries
                last_newline = text.rfind('\n', end - 50, end)
                if last_newline != -1:
                    end = last_newline
                else:
                    last_space = text.rfind(' ', end - 20, end)
                    if last_space != -1:
                        end = last_space
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
                
            start = end - self.chunk_overlap
            if start < 0:
                start = 0
            
            # Avoid infinite loop if overlap >= size
            if end <= start:
                start = end
                
        return chunks

    def process_pdf(self, file_content, filename):
        """Complete pipeline: Extract -> Chunk -> Format as documents."""
        text = self.extract_text_from_pdf(file_content)
        chunks = self.chunk_text(text)
        
        documents = []
        for i, chunk in enumerate(chunks):
            # We format it to match the existing schema in VectorStore
            # 'question' is used for the vector search metadata display
            # 'answer' contains the full text chunk
            documents.append({
                "question": f"Snippet from {filename} (Part {i+1})",
                "answer": chunk,
                "source": filename,
                "type": "document_chunk"
            })
        return documents

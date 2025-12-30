
import io
import pytesseract
from PIL import Image
import pdfplumber
from docx import Document

class DocumentProcessor:
    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        text = ""
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text

    def extract_text_from_docx(self, file_bytes: bytes) -> str:
        doc = Document(io.BytesIO(file_bytes))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text

    def extract_text_from_image(self, file_bytes: bytes) -> str:
        image = Image.open(io.BytesIO(file_bytes))
        # Note: Tesseract binary must be in PATH or configured specifically
        try:
            text = pytesseract.image_to_string(image)
        except Exception as e:
            return f"Error using Tesseract OCR: {str(e)}. Ensure Tesseract is installed."
        return text

    def process_file(self, file_bytes: bytes, file_ext: str) -> str:
        file_ext = file_ext.lower()
        if file_ext == '.pdf':
            return self.extract_text_from_pdf(file_bytes)
        elif file_ext in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_bytes)
        elif file_ext in ['.jpg', '.jpeg', '.png']:
            return self.extract_text_from_image(file_bytes)
        elif file_ext == '.txt':
            return file_bytes.decode('utf-8')
        else:
            return "Unsupported file format."

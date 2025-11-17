import io
import zipfile
from docx import Document
from PyPDF2 import PdfReader


class ResumeParser:
    """
    Strict resume parser supporting ONLY:
    - PDF
    - DOCX

    Automatically rejects other formats.
    """

    @staticmethod
    def parse(file_bytes: bytes) -> str:
        """
        Detect file type and extract text.
        """

        # -------- TRY PDF FIRST --------
        try:
            pdf = PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            if text.strip():  # PDF success
                return text
        except Exception:
            pass  # Not a PDF → try DOCX

        # -------- TRY DOCX --------
        try:
            stream = io.BytesIO(file_bytes)
            if zipfile.is_zipfile(stream):
                doc = Document(stream)
                return "\n".join([p.text for p in doc.paragraphs])
        except Exception:
            pass

        # -------- INVALID FILE TYPE --------
        return "UNSUPPORTED_FILE_TYPE"

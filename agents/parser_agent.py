from tools.pdf_parser import ResumeParser

class ResumeParserAgent:
    def __init__(self, session):
        self.session = session

    def run(self, resume_bytes):
        text = ResumeParser.parse(resume_bytes)

        if text == "UNSUPPORTED_FILE_TYPE":
            raise ValueError("Only PDF or DOCX resume formats are supported.")

        self.session.set("resume_text", text)
        return text

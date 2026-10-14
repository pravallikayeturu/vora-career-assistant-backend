from pypdf import PdfReader


def extract_resume_text(resume_file):
    reader = PdfReader(resume_file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text
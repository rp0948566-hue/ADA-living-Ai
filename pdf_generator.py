
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

class PDFCreator:
    def __init__(self, output_path):
        self.output_path = output_path
        self.styles = getSampleStyleSheet()

    def create_pdf(self, content, title="Document", author="ADA"):
        doc = SimpleDocTemplate(self.output_path, pagesize=letter)
        story = []

        # TODO: Add title and author metadata
        # TODO: Implement more advanced styling (headings, fonts, etc.)
        # TODO: Add ability to use templates

        for line in content.split("\n"):
            story.append(Paragraph(line, self.styles["Normal"]))
            story.append(Spacer(1, 0.18 * inch))

        doc.build(story)
        return self.output_path

# app/services/presentation_service.py
import re
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt

# Define storage path
PRESENTATION_DIR = Path("app/storage/presentations")
PRESENTATION_DIR.mkdir(parents=True, exist_ok=True)

class PresentationService:
    """Service for creating well-structured and paginated PowerPoint presentations."""

    def _clean_text(self, text: str) -> str:
        """Removes markdown-like formatting for presentation."""
        text = re.sub(r'^\s*([\*\-]|\d+\.)\s*', '', text)
        text = re.sub(r'^\s*#+\s*', '', text)
        text = text.replace('**', '').replace('*', '')
        return text.strip()

    def _paginate_content(self, lines: list[str], max_words: int, max_chars: int) -> list[list[str]]:
        """
        Splits a list of lines into multiple pages based on word and character limits.
        """
        pages = []
        current_page_lines = []
        current_word_count = 0
        current_char_count = 0

        for line in lines:
            line_word_count = len(line.split())
            line_char_count = len(line)

            # If adding the new line exceeds limits, finalize the current page
            if current_page_lines and (current_word_count + line_word_count > max_words or current_char_count + line_char_count > max_chars):
                pages.append(current_page_lines)
                # Start a new page
                current_page_lines = [line]
                current_word_count = line_word_count
                current_char_count = line_char_count
            else:
                # Add to the current page
                current_page_lines.append(line)
                current_word_count += line_word_count
                current_char_count += line_char_count
        
        # Add the last remaining page
        if current_page_lines:
            pages.append(current_page_lines)
            
        return pages

    def create_presentation_from_summary(self, document_id: str, summary_text: str) -> Path:
        """
        Creates a .pptx presentation from a structured summary, with intelligent
        title parsing and content pagination.
        """
        prs = Presentation()
        title_slide_layout = prs.slide_layouts[0]
        content_slide_layout = prs.slide_layouts[1]

        # --- Title Slide ---
        slide = prs.slides.add_slide(title_slide_layout)
        title = slide.shapes.title
        title.text = "Presentation Summary"
        if len(slide.placeholders) > 1:
            slide.placeholders[1].text = f"Generated from document: {document_id}"

        # --- Section Splitting ---
        section_pattern = re.compile(r'\n(?=\s*(?:[IVXLCDM]+\.|\d+\.)\s+)', re.IGNORECASE)
        sections = section_pattern.split(summary_text.strip())

        # --- Create Content Slides ---
        for section_text in sections:
            lines = [line.strip() for line in section_text.strip().split('\n') if line.strip()]
            if not lines:
                continue

            # --- Intelligent Title Parsing ---
            title_line = lines.pop(0)
            title_match = re.match(r'^\s*(?:[IVXLCDM]+\.|\d+\.)\s*(.*)', title_line)
            slide_title = self._clean_text(title_match.group(1) if title_match else title_line)

            # --- Paginate Body Content ---
            body_lines = [self._clean_text(line) for line in lines]
            paginated_body = self._paginate_content(body_lines, max_words=100, max_chars=528)

            if not paginated_body: # Handle sections with only a title
                paginated_body.append([])

            # --- Create a Slide for Each Page ---
            for i, page_lines in enumerate(paginated_body):
                slide = prs.slides.add_slide(content_slide_layout)
                title_shape = slide.shapes.title
                body_shape = slide.placeholders[1]
                
                # Add "(continued)" for subsequent slides of the same section
                title_shape.text = f"{slide_title} (lanjutan)" if i > 0 else slide_title
                
                text_frame = body_shape.text_frame
                text_frame.clear()
                
                if not page_lines:
                    p = text_frame.add_paragraph()
                    p.text = "(No additional content for this section)"
                    p.font.italic = True
                else:
                    for line in page_lines:
                        p = text_frame.add_paragraph()
                        p.text = line
                        p.level = 0
                        p.font.size = Pt(16)

        # --- Save Presentation ---
        file_path = PRESENTATION_DIR / f"{document_id}.pptx"
        prs.save(file_path)
        
        return file_path

# Create a singleton instance
presentation_service = PresentationService()
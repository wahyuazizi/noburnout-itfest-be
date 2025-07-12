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
        Splits text content into multiple pages based on word and character limits,
        ensuring no page is overly dense.
        """
        pages = []
        # Join and clean all lines, then split into words to handle long paragraphs
        full_text = " ".join(self._clean_text(line) for line in lines)
        words = full_text.split()

        if not words:
            return []

        current_page_words = []
        for word in words:
            # Check if adding the next word would exceed the limits
            if current_page_words and (
                len(" ".join(current_page_words) + " " + word) > max_chars or
                len(current_page_words) + 1 > max_words
            ):
                # Finalize the current page and start a new one
                pages.append([" ".join(current_page_words)])
                current_page_words = [word]
            else:
                current_page_words.append(word)

        # Add the last remaining page
        if current_page_words:
            pages.append([" ".join(current_page_words)])

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
            
            raw_title = title_match.group(1) if title_match else title_line
            slide_title_full = self._clean_text(raw_title)
            
            # Shorten title to a max of 5 words for conciseness
            title_words = slide_title_full.split()
            if len(title_words) > 5:
                slide_title = ' '.join(title_words[:5]) + '...'
            else:
                slide_title = slide_title_full

            # --- Paginate Body Content ---
            paginated_body = self._paginate_content(lines, max_words=50, max_chars=275)

            if not paginated_body: # Skip sections with no content
                continue

            # --- Create a Slide for Each Page ---
            for i, page_lines in enumerate(paginated_body):
                slide = prs.slides.add_slide(content_slide_layout)
                title_shape = slide.shapes.title
                body_shape = slide.placeholders[1]
                
                # Add "(continued)" for subsequent slides of the same section
                title_shape.text = f"{slide_title} (lanjutan)" if i > 0 else slide_title
                
                text_frame = body_shape.text_frame
                text_frame.clear()
                
                # This check is now redundant due to the continue above, but kept for safety
                if not page_lines:
                    continue
                
                for line in page_lines:
                    p = text_frame.add_paragraph()
                    p.text = line
                    p.level = 0
                    p.font.size = Pt(18)

        # --- Save Presentation ---
        file_path = PRESENTATION_DIR / f"{document_id}.pptx"
        prs.save(file_path)
        
        return file_path

# Create a singleton instance
presentation_service = PresentationService()
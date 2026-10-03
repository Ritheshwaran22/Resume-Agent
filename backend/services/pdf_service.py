import re
import logging
import pymupdf as fitz
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

class PDFExtractionService:
    @staticmethod
    def validate_file(uploaded_file):
        """
        Validates file size, extension, and content type.
        """
        if not uploaded_file:
            raise ValidationError("No file was uploaded.")

        if uploaded_file.size > MAX_FILE_SIZE:
            raise ValidationError("File size exceeds 10 MB limit.")

        if uploaded_file.size == 0:
            raise ValidationError("The uploaded file is empty.")

        filename = uploaded_file.name.lower()
        if not filename.endswith('.pdf'):
            raise ValidationError("Only PDF files (.pdf) are supported.")

        content_type = getattr(uploaded_file, 'content_type', '')
        if content_type and content_type not in ['application/pdf', 'application/x-pdf', 'application/acrobat', 'application/octet-stream']:
            if not filename.endswith('.pdf'):
                raise ValidationError("Invalid file type. Only PDF documents are allowed.")

    @classmethod
    def extract_text(cls, uploaded_file) -> str:
        """
        Safely opens and extracts text from an uploaded PDF using PyMuPDF.
        Preserves reading order by sorting text blocks vertically and horizontally.
        Handles encrypted, corrupted, scanned, and empty PDFs.
        """
        cls.validate_file(uploaded_file)

        try:
            # Read bytes into memory
            file_bytes = uploaded_file.read()
            uploaded_file.seek(0)  # Reset stream position

            doc = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as e:
            logger.warning(f"Corrupted or invalid PDF upload: {e}")
            raise ValidationError("The uploaded file is corrupted or not a valid PDF.")

        if doc.is_encrypted:
            doc.close()
            raise ValidationError("The PDF is password-protected. Please upload an unlocked PDF.")

        if doc.page_count == 0:
            doc.close()
            raise ValidationError("The uploaded PDF contains no pages.")

        extracted_pages = []
        total_images = 0

        page_count = doc.page_count
        for page_idx in range(page_count):
            try:
                page = doc.load_page(page_idx)
                # Extract text blocks: (x0, y0, x1, y1, text, block_no, block_type)
                # block_type == 0 indicates text
                blocks = page.get_text("blocks")
                text_blocks = [b for b in blocks if b[6] == 0]
                # Sort blocks by vertical position (y0), then horizontal position (x0) to preserve reading order
                text_blocks.sort(key=lambda b: (b[1], b[0]))
                page_text = "\n".join(b[4].strip() for b in text_blocks if b[4].strip())
                extracted_pages.append(page_text)
                total_images += len(page.get_images())
            except Exception as page_err:
                logger.warning(f"Failed extracting text from page {page_idx}: {page_err}")
                continue

        doc.close()

        full_text = "\n\n".join(extracted_pages).strip()
        # Clean non-printable control characters (except newline, tab, carriage return)
        full_text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', full_text)
        # Normalize excessive blank lines
        full_text = re.sub(r'\n{3,}', '\n\n', full_text)

        # Check for image-only or unextractable PDF
        alphanumeric_count = len(re.findall(r'[a-zA-Z0-9]', full_text))
        if alphanumeric_count < 25:
            if total_images > 0:
                raise ValidationError(
                    "This PDF appears to be a scanned or image-only document. "
                    "Please upload a standard text PDF resume with selectable text."
                )
            raise ValidationError(
                "Could not extract sufficient text from this PDF. "
                "Please verify that the document contains readable text."
            )

        logger.info(
            f"[PDFExtractionService] Extracted {len(full_text)} characters from '{uploaded_file.name}' "
            f"({page_count} pages, {alphanumeric_count} alphanumeric chars)."
        )
        return full_text

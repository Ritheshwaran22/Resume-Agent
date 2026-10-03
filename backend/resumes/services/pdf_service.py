"""
PDF Processing Service.
Re-exports the active PDFExtractionService from services.pdf_service.
"""
from services.pdf_service import PDFExtractionService

def extract_text_from_pdf(uploaded_file):
    """Convenience functional wrapper for PDF extraction."""
    return PDFExtractionService.extract_text(uploaded_file)

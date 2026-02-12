#!/usr/bin/env python3
"""
Script to extract text from .docx files in the document-update folder.
"""

import os
import sys
from pathlib import Path

try:
    from docx import Document
except ImportError:
    print("python-docx not installed. Installing...")
    os.system(f"{sys.executable} -m pip install python-docx -q")
    from docx import Document

def extract_text_from_docx(file_path):
    """Extract all text from a .docx file."""
    try:
        doc = Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text)
        return "\n".join(text)
    except Exception as e:
        return f"Error reading {file_path}: {str(e)}"

def main():
    import io
    import sys
    
    # Set UTF-8 encoding for output
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    current_dir = Path(__file__).parent
    docx_files = list(current_dir.glob("*.docx"))
    
    if not docx_files:
        print("No .docx files found in the directory.")
        return
    
    print(f"Found {len(docx_files)} .docx files\n")
    print("=" * 80)
    
    for docx_file in sorted(docx_files):
        print(f"\n{'=' * 80}")
        print(f"FILE: {docx_file.name}")
        print(f"{'=' * 80}\n")
        text = extract_text_from_docx(docx_file)
        print(text)
        print("\n")

if __name__ == "__main__":
    main()


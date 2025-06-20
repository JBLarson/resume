#!/usr/bin/env python3
"""
Convert a PDF’s first page to a JPEG image.
Usage:
    python3 pdf2jpg.py input.pdf
Produces:
    input.jpg
Dependencies:
    pip install pdf2image
    # On macOS/Linux, you may also need poppler installed:
    #   brew install poppler       (macOS)
    #   sudo apt-get install poppler-utils  (Ubuntu/Debian)
"""

import argparse
from pdf2image import convert_from_path

def pdf_to_jpeg(pdf_path: str):
    # Convert all pages; we’ll save only the first one
    pages = convert_from_path(pdf_path, dpi=200)
    if not pages:
        raise RuntimeError(f"No pages found in '{pdf_path}'")
    out_path = pdf_path.rsplit('.', 1)[0] + '.jpg'
    pages[0].save(out_path, 'JPEG')
    print(f"Saved JPEG: {out_path}")

def main():
    parser = argparse.ArgumentParser(description="Convert PDF to JPEG")
    parser.add_argument('pdf', help="Path to the input PDF file")
    args = parser.parse_args()
    pdf_to_jpeg(args.pdf)

if __name__ == '__main__':
    main()

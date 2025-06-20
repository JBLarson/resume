# /toPdf.py

import asyncio
import os
from pyppeteer import launch

async def toPDF(html_file, pdf_file):
    """
    Converts a local HTML file to a high-fidelity PDF that mirrors the
    on-screen appearance.
    """
    if not os.path.exists(html_file):
        print(f"Error: The file '{html_file}' was not found.")
        return

    print("--- Launching Headless Browser ---")
    browser = await launch(
        # Some systems require these args to run Chrome headlessly
        args=['--no-sandbox', '--disable-setuid-sandbox']
    )
    page = await browser.newPage()

    # 1. Set a realistic, high-resolution viewport
    # This ensures the two-column layout renders correctly
    print("--- Setting Viewport ---")
    await page.setViewport({'width': 1280, 'height': 1080, 'deviceScaleFactor': 2})

    # 2. **THIS IS THE KEY STEP**
    # Force the page to render using screen media styles, not print styles
    print("--- Emulating Screen Media ---")
    await page.emulateMedia(mediaType='screen')

    html_path = f"file://{os.path.abspath(html_file)}"
    print(f"--- Navigating to {html_path} ---")

    # 3. Wait until all network resources (CSS, fonts) are fully loaded
    await page.goto(html_path, {'waitUntil': 'networkidle0'})

    print("--- Generating PDF ---")
    # 4. Generate the PDF with options for perfect fidelity
    await page.pdf({
        'path': pdf_file,
        'width': '1280px', # Match the viewport width
        'height': '1664px', # Approximate height for this resume, can be adjusted
        'printBackground': True, # Crucial for rendering background colors
        'pageRanges': '1', # Ensure only the first page is printed
        'margin': { # Remove default headers, footers, and margins
            'top': '0',
            'right': '0',
            'bottom': '0',
            'left': '0'
        }
    })

    print("--- Closing Browser ---")
    await browser.close()
    print(f"\n✅ Success! Pixel-perfect PDF generated: {pdf_file}")

if __name__ == "__main__":
    input_html = "index.html"
    output_pdf = "JB_Larson_Resume.pdf"

    asyncio.get_event_loop().run_until_complete(
        toPDF(input_html, output_pdf)
    )

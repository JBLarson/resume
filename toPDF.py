import asyncio
import os
from pyppeteer import launch
from fpdf import FPDF

async def toPDF(html_file: str, pdf_file: str):
    """
    1. Renders index.html in headless Chrome.
    2. Screenshots the resume container (exact layout).
    3. Embeds that PNG on a single Letter‐size PDF page.
    """
    if not os.path.exists(html_file):
        print(f"Error: '{html_file}' not found.")
        return

    browser = await launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
    page = await browser.newPage()
    await page.setViewport({"width": 1280, "height": 800, "deviceScaleFactor": 2})
    await page.emulateMedia("screen")
    await page.goto(f"file://{os.path.abspath(html_file)}", {"waitUntil": "networkidle0"})

    # Grab just the resume card
    handle = await page.querySelector(".shadow-2xl")
    png_path = "resume.png"
    await handle.screenshot({"path": png_path, "omitBackground": False})

    await browser.close()

    # Now embed into a Letter PDF
    pdf = FPDF(unit="pt", format="letter")
    pdf.add_page()
    # Letter width = 612pt; auto scale height to preserve aspect ratio
    pdf.image(png_path, x=0, y=0, w=612)
    pdf.output(pdf_file)
    print(f"✅ PDF written to {pdf_file} (via screenshot)")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(
        toPDF("index.html", "JB_Larson_Resume.pdf")
    )

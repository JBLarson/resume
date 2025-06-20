import config
from scraper import fetch_url
from parser import extract_job_text
from nlp import extract_keywords, filter_and_rank
from resume_builder import load_template, inject_keywords, save_html
import subprocess

def main(job_url: str):
    html = fetch_url(job_url)
    job_text = extract_job_text(html)

    raw_terms = extract_keywords(job_text)
    keywords = filter_and_rank(raw_terms)

    tmpl = load_template(config.RESUME_TEMPLATE)
    updated_html = inject_keywords(tmpl, keywords)
    save_html(updated_html, config.OUTPUT_HTML)

    # (Re-use your toPDF.py logic)
    subprocess.run(["python3", "toPdf.py",
                    config.OUTPUT_HTML, config.OUTPUT_PDF], check=True)
    print("✅ Resume updated and PDF generated.")

if __name__ == "__main__":
    import sys
    main(sys.argv[1])

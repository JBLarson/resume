from jinja2 import Environment, FileSystemLoader
from typing import List

def load_template(path: str):
    env = Environment(loader=FileSystemLoader("."))
    return env.get_template(path)

def inject_keywords(template, keywords: List[str], section: str = "skills") -> str:
    """
    Render HTML with `dynamic_skills=keywords` for the sidebar.
    Could also replace placeholders in bullet points.
    """
    return template.render(dynamic_skills=keywords)

def save_html(html: str, out_path: str):
    with open(out_path, "w") as f:
        f.write(html)

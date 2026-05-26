from pathlib import Path

from jinja2 import Environment
import mistune
import nh3
import pyhuml

env = Environment(autoescape=True)
template = env.from_string(Path('template.html').read_text())

def reload_template():
    global template
    template = env.from_string(Path('template.html').read_text())


def render_markdown(md_file_text: str) -> str:
    context = {}
    
    parts = md_file_text.split('\n---', maxsplit=1)
    if len(parts)==2:
        context = pyhuml.loads(parts[0])
    
    context['content'] = nh3.clean(mistune.html(parts[-1]))
    return template.render(**context)
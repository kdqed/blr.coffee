from pathlib import Path
import sys

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


def build():
    for path in Path('.').rglob('*.html.md'):
        target = path.with_suffix('')
        to_write = False
        if not target.exists():
            to_write = True
        elif path.stat().st_mtime > target.stat().st_mtime:
            to_write = True
        elif '-f' in sys.argv:
            to_write = True
        
        if to_write:
            print('[generating]', target)
            content = render_markdown(path.read_text())
            target.write_text(content)
        

        
if __name__ == "__main__":
    build()
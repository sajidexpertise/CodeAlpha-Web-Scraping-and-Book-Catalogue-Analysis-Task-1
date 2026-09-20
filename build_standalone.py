"""Bundle Nexus dashboard code and data into one offline-friendly HTML file."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DASH = ROOT / "dashboard"


def build() -> Path:
    html = (DASH / "index.html").read_text(encoding="utf-8")
    data = (DASH / "data.js").read_text(encoding="utf-8").replace("<", "\\u003c")
    app = (DASH / "app.js").read_text(encoding="utf-8")
    assert 'src="data.js"' in html and 'src="app.js"' in html
    html = re.sub(r'<script defer src="(?:data|app)\.js"></script>', "", html)
    assert 'src="data.js"' not in html and 'src="app.js"' not in html
    html = html.replace("</body>", "<script>\n" + data + "\n</script>\n<script>\n" + app + "\n</script>\n</body>")
    out = ROOT / "OPEN_DASHBOARD.html"
    out.write_text(html, encoding="utf-8")
    print(f"Built standalone dashboard: {out.name} ({out.stat().st_size:,} bytes)")
    return out


if __name__ == "__main__":
    build()

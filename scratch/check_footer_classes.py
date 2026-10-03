import glob
import re

for f in sorted(glob.glob("*.html")):
    txt = open(f, encoding="utf-8").read()
    m = re.search(r'<footer class="site-footer">\s*<div class="([^"]+)"', txt)
    if m:
        print(f, "-->", m.group(1))

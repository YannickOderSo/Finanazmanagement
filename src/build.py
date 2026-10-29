"""Assemble the Lernpfad page from its parts and insert the generated charts."""
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
parts = sorted(glob.glob(os.path.join(HERE, "parts", "p*.html")))
html = "".join(open(p).read() for p in parts)


def chart(m):
    path = os.path.join(HERE, "charts", m.group(1) + ".svg")
    return open(path).read()


html = re.sub(r"\{\{chart:([a-z]+)\}\}", chart, html)
missing = re.findall(r"\{\{[^}]+\}\}", html)
assert not missing, missing
out = os.path.join(HERE, "Finanzmanagement-Lernpfad.html")
open(out, "w").write(html)
print(out, len(html), "bytes from", [os.path.basename(p) for p in parts])

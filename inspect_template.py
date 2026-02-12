"""Inspect the template DOCX to extract exact formatting specs."""
from docx import Document
from docx.oxml.ns import qn
import lxml.etree as ET
import zipfile, io, re

doc = Document('document-update/Lesson Objectives Generator.docx')

# Extract theme from ZIP
buf = io.BytesIO()
doc.save(buf)
buf.seek(0)
z = zipfile.ZipFile(buf)
for name in z.namelist():
    if 'theme' in name.lower() and name.endswith('.xml'):
        theme_data = z.read(name).decode()
        root = ET.fromstring(theme_data.encode())
        ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
        major = root.find('.//a:majorFont/a:latin', ns)
        minor = root.find('.//a:minorFont/a:latin', ns)
        if major is not None:
            print("Major font:", major.get("typeface"))
        if minor is not None:
            print("Minor font:", minor.get("typeface"))
        
        scheme = root.find('.//a:clrScheme', ns)
        if scheme is not None:
            print("\nTheme colors:")
            for child in scheme:
                tag = child.tag.split('}')[-1]
                for c in child:
                    ct = c.tag.split('}')[-1]
                    val = c.get('val') or c.get('lastClr')
                    print("  %s: %s=%s" % (tag, ct, val))

# Heading 2 style
print("\n=== HEADING 2 STYLE ===")
for style in doc.styles:
    if style.name == 'Heading 2':
        xml = ET.tostring(style.element, pretty_print=True).decode()
        rpr = re.search(r'<w:rPr.*?</w:rPr>', xml, re.DOTALL)
        ppr = re.search(r'<w:pPr.*?</w:pPr>', xml, re.DOTALL)
        if rpr:
            print("rPr:", rpr.group())
        if ppr:
            print("pPr:", ppr.group())
        break

# Title style color
print("\n=== TITLE STYLE ===")
for style in doc.styles:
    if style.name == 'Title':
        xml = ET.tostring(style.element, pretty_print=True).decode()
        rpr = re.search(r'<w:rPr.*?</w:rPr>', xml, re.DOTALL)
        if rpr:
            print("rPr:", rpr.group())
        break

# Paragraph 6 (stem) formatting
print("\n=== PARAGRAPH 6 (stem) ===")
p6 = doc.paragraphs[6]
for i, run in enumerate(p6.runs):
    xml = ET.tostring(run._element, pretty_print=True).decode()
    # Strip namespaces noise
    short = re.sub(r' xmlns:[^=]+="[^"]*"', '', xml)
    print("Run %d: %s" % (i, short.strip()))

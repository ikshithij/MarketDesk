"""Build the research paper with the bundled python-docx runtime.
Equations are rendered by render_paper_equations.cjs before this command.
"""
import argparse, json, re
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

parser=argparse.ArgumentParser()
parser.add_argument('--equation-dir',required=True)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
source=root/'docs/papers/MarketDesk_Research_Methods_v1.0.md'
out=source.with_suffix('.docx')
equations=json.loads((Path(args.equation_dir)/'manifest.json').read_text())
doc=Document();sec=doc.sections[0]
sec.page_width=Inches(8.5);sec.page_height=Inches(11)
sec.top_margin=Inches(.78);sec.bottom_margin=Inches(.75);sec.left_margin=Inches(.82);sec.right_margin=Inches(.82)
sec.header_distance=Inches(.3);sec.footer_distance=Inches(.3)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Header','Footer']:
 style=doc.styles[name];style.font.name='Calibri';style.font.color.rgb=RGBColor(0,0,0)
 style.element.rPr.rFonts.set(qn('w:eastAsia'),'Calibri')
 for color in list(style.element.xpath('.//w:color')):
  for attr in ['themeColor','themeTint','themeShade']:color.attrib.pop(qn('w:'+attr),None)
normal=doc.styles['Normal'];normal.font.size=Pt(11);normal.paragraph_format.line_spacing=1.12;normal.paragraph_format.space_after=Pt(7)
for name,size,before,after in [('Title',25,0,12),('Heading 1',16,18,9),('Heading 2',12,13,7)]:
 st=doc.styles[name];st.font.size=Pt(size);st.font.bold=name!='Title';st.paragraph_format.space_before=Pt(before);st.paragraph_format.space_after=Pt(after);st.paragraph_format.keep_with_next=True
for pPr in doc.styles['Title'].element.xpath('.//w:pBdr'):
 pPr.getparent().remove(pPr)
header=sec.header.paragraphs[0];header.text='MarketDesk Research Methods';header.style='Header';header.runs[0].font.size=Pt(9)
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
r=footer.add_run('Version 1.0   |   ');r.font.size=Pt(9)
f=OxmlElement('w:fldSimple');f.set(qn('w:instr'),'PAGE');footer._p.append(f)
doc.core_properties.title='MarketDesk Research Methods and Strategy Standard'
doc.core_properties.subject='Research evidence and versioned methods for MarketDesk'
doc.core_properties.author='MarketDesk'
doc.core_properties.version='1.0'

def text(p,value):
 # Retain clickable URLs in references without manually coloured title formatting.
 for part in re.split(r'(https?://\S+)',value):
  if part.startswith('http'):
   link=OxmlElement('w:hyperlink');link.set(qn('r:id'),p.part.relate_to(part,RT.HYPERLINK,is_external=True))
   run=OxmlElement('w:r');props=OxmlElement('w:rPr');color=OxmlElement('w:color');color.set(qn('w:val'),'24465A');props.append(color);run.append(props)
   t=OxmlElement('w:t');t.text=part;run.append(t);link.append(run);p._p.append(link)
  else:p.add_run(part)

def table(rows):
 t=doc.add_table(rows=1,cols=len(rows[0]));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
 widths=[1.45,3.05,2.36]
 pr=t._tbl.tblPr;b=OxmlElement('w:tblBorders')
 for edge in ['top','left','bottom','right','insideH','insideV']:
  el=OxmlElement('w:'+edge);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'D9D9D9');b.append(el)
 pr.append(b)
 for ri,row in enumerate(rows):
  cells=t.rows[0].cells if ri==0 else t.add_row().cells
  trpr=t.rows[ri]._tr.get_or_add_trPr();cant=OxmlElement('w:cantSplit');trpr.append(cant)
  if ri==0:repeat=OxmlElement('w:tblHeader');trpr.append(repeat)
  for ci,value in enumerate(row):
   cell=cells[ci];cell.width=Inches(widths[ci]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   tcpr=cell._tc.get_or_add_tcPr();margins=OxmlElement('w:tcMar')
   for edge,val in [('top',90),('bottom',90),('left',110),('right',110)]:
    el=OxmlElement('w:'+edge);el.set(qn('w:w'),str(val));el.set(qn('w:type'),'dxa');margins.append(el)
   tcpr.append(margins)
   shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'253747' if ri==0 else 'F3F5F6' if ri%2==0 else 'FFFFFF');tcpr.append(shade)
   p=cell.paragraphs[0];p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=1.05
   r=p.add_run(value);r.font.size=Pt(10);r.bold=ri==0;r.font.color.rgb=RGBColor.from_string('FFFFFF' if ri==0 else '000000')
 doc.add_paragraph().paragraph_format.space_after=Pt(0)

lines=source.read_text().splitlines();i=0;eq=0
while i<len(lines):
 line=lines[i].strip()
 if not line:i+=1;continue
 if line.startswith('$$'):
  item=equations[eq];p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
  pic=p.add_run().add_picture(str(Path(args.equation_dir)/item['file']),width=Inches(item['width_inches']))
  pic._inline.docPr.set('descr',item['latex']);p.paragraph_format.space_before=Pt(8);p.paragraph_format.space_after=Pt(10)
  eq+=1;i+=1;continue
 if line.startswith('|'):
  rows=[]
  while i<len(lines) and lines[i].strip().startswith('|'):
   cells=[x.strip() for x in lines[i].strip().strip('|').split('|')]
   if not all(re.fullmatch(r'[:\-\s]+',c) for c in cells):rows.append(cells)
   i+=1
  table(rows);continue
 if line.startswith('# '):doc.add_paragraph(line[2:],'Title');i+=1;continue
 if line.startswith('## '):doc.add_paragraph(line[3:],'Heading 1');i+=1;continue
 if line.startswith('### '):doc.add_paragraph(line[4:],'Heading 2');i+=1;continue
 p=doc.add_paragraph()
 if line.startswith('Evidence review'):
  p.paragraph_format.space_after=Pt(9);r=p.add_run(line);r.font.size=Pt(13)
 elif line.startswith('Version 1.0'):
  r=p.add_run(line);r.font.size=Pt(10);p.paragraph_format.space_after=Pt(14)
 else:text(p,line)
 i+=1
# Widow/orphan control applies to body paragraphs without keeping long passages together.
for p in doc.paragraphs:
 p.paragraph_format.widow_control=True
out.parent.mkdir(parents=True,exist_ok=True);doc.save(out)
print(str(out));print('Words:',len(source.read_text().split()))

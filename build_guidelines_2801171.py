#!/usr/bin/env python3
"""Build contest 2801171 deliverables with existing PyMuPDF/Pillow/fontTools.

No logo edits, external runtimes or package installation. Font files live in assets/fonts.
Run: python3 build_guidelines_2801171.py
"""
from pathlib import Path
import hashlib
import html
import json
import math
import re
import shutil
import struct
import zipfile
import xml.etree.ElementTree as ET

import fitz
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parent
A, E, T = ROOT / 'assets', ROOT / 'exports', ROOT / 'tmp/pdfs'
F = A / 'fonts'
for directory in (E, T):
    directory.mkdir(parents=True, exist_ok=True)
LOGO = A / 'papua_logo_cropped.png'
LOGO_HASH = hashlib.sha256(LOGO.read_bytes()).hexdigest()
PDF_NAME = 'Papua_Diving_Resorts_Brand_Guidelines_2026.pdf'
ZIP_NAME = 'Papua_Diving_Resorts_2026_Brand_Kit.zip'
PALETTE = [
    ('Papua Brown', '#7E2F19', (24,83,91,29), 'Master brand / major headings'),
    ('Bark Clay', '#A65A2A', (22,65,86,12), 'Warm accents / calls to action'),
    ('Ochre Clay', '#C98A5B', (17,46,68,3), 'Highlights / graphic detail'),
    ('Sandstone', '#DCCAAF', (13,18,31,0), 'Kri base / tactile fields'),
    ('Coral Sand', '#EFE5D6', (5,8,14,0), 'Secondary neutral / panels'),
    ('Natural Linen', '#F6F1EB', (3,4,7,0), 'Primary field / logo holding shape'),
    ('Bark Charcoal', '#2B2A27', (69,63,67,72), 'Body copy / dark neutral'),
    ('Sago Leaf', '#A8B69A', (36,19,41,2), 'Kri accent / conservation cues'),
    ('Lagoon Reef Teal', '#1A5E63', (85,34,42,18), 'Sorido accent only'),
]
BROWN, CLAY, OCHRE, SAND, CORAL, LINEN, CHAR, SAGO, TEAL = [p[1] for p in PALETTE]


def rgb(h):
    return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))


def contrast(a,b):
    def lum(h):
        c = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb(h)]
        return sum(v*w for v,w in zip(c,(.2126,.7152,.0722)))
    x,y=sorted((lum(a),lum(b)))
    return (y+.05)/(x+.05)


def motif(name, w, h, body, desc):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{name.replace("_"," ")}</title><desc>{desc}</desc>{body}</svg>'
    (E/f'{name}.svg').write_text(svg)
    doc=fitz.open(stream=svg.encode(),filetype='svg')
    pdoc=fitz.open('pdf',doc.convert_to_pdf())
    pix=pdoc[0].get_pixmap(matrix=fitz.Matrix(4,4),alpha=True)
    out=E/f'{name}.png'
    pix.save(out)
    with Image.open(out) as im:
        im.save(out,dpi=(300,300))
    return name


def build_motifs():
    # Repeated chevrons, nested diamonds and dotted bands from the supplied bark studies.
    parts=[f'<path d="M0 12H1200 M0 148H1200" fill="none" stroke="{BROWN}" stroke-width="4"/>']
    for x in range(0,1200,100):
        parts += [f'<path d="M{x+6} 35L{x+50} 79L{x+94} 35 M{x+6} 82L{x+50} 126L{x+94} 82" fill="none" stroke="{CLAY}" stroke-width="9" stroke-linejoin="miter"/>',
                  f'<path d="M{x+50} 39L{x+63} 52L{x+50} 65L{x+37} 52Z" fill="{BROWN}"/>',
                  f'<circle cx="{x+16}" cy="135" r="3" fill="{BROWN}"/><circle cx="{x+84}" cy="135" r="3" fill="{BROWN}"/>']
    names=[motif('Papuan_Bark_Chevron_Border',1200,160,''.join(parts),'Original bark-inspired geometric border. Referenced to employer bark paintings; no traditional or sacred meaning claimed.')]
    waves=[]
    for y,c in [(30,BROWN),(65,CLAY),(100,OCHRE)]:
        d=f'M0 {y}'
        for x in range(0,1200,200):
            d+=f'C{x+45} {y-25} {x+55} {y-25} {x+100} {y}C{x+145} {y+25} {x+155} {y+25} {x+200} {y}'
        waves.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="5" stroke-linecap="butt"/>')
    names.append(motif('Raja_Ampat_Current_Wave_Divider',1200,130,''.join(waves),'Original contemporary reef-current divider. Secondary to bark geometry; not a traditional cultural symbol.'))
    corner=f'<g fill="none" stroke-linejoin="miter"><path d="M18 282V18H282 M40 260V40H260" stroke="{BROWN}" stroke-width="6"/><path d="M68 228V68H228 M92 204V92H204" stroke="{CLAY}" stroke-width="8"/><path d="M120 176V120H176" stroke="{OCHRE}" stroke-width="6"/><path d="M182 150L214 182L182 214L150 182Z M182 166L198 182L182 198L166 182Z" stroke="{BROWN}" stroke-width="5"/></g>'
    names.append(motif('Sorido_Kri_Corner_Emblem',300,300,corner,'Shared bark-inspired editorial corner ornament for both resorts. Decorative asset, never a replacement logo.'))
    return names


FONTS={k:fitz.Font(fontfile=str(F/v)) for k,v in {'tenor':'TenorSans-Regular.ttf','body':'SourceSans3-Regular.ttf','medium':'SourceSans3-Medium.ttf','semi':'SourceSans3-SemiBold.ttf'}.items()}
FONT_FILES={'tenor':'TenorSans-Regular.ttf','body':'SourceSans3-Regular.ttf','medium':'SourceSans3-Medium.ttf','semi':'SourceSans3-SemiBold.ttf'}
W,H=595.276,841.89
doc=fitz.open()
page_titles=[]
text_bounds=[]


def rect(p,x,y,w,h,c,stroke=None,r=0):
    p.draw_rect(fitz.Rect(x,y,x+w,y+h),color=rgb(stroke) if stroke else None,fill=rgb(c) if c else None,width=.6,radius=r or None)


def line(p,x,y,x2,y2,c=SAND,width=.7,dashes=None):
    p.draw_line((x,y),(x2,y2),color=rgb(c),width=width,dashes=dashes)


def txt(p,s,x,y,size=10.5,font='body',color=CHAR,tracking=0):
    p.insert_font(fontname=font,fontfile=str(F/FONT_FILES[font]))
    width=FONTS[font].text_length(s,fontsize=size)+max(0,len(s)-1)*tracking*size
    if x+width>W-20: raise ValueError(f'Text exceeds page: {s}')
    if tracking:
        pos=x
        for ch in s:
            p.insert_text((pos,y+size),ch,fontsize=size,fontname=font,color=rgb(color))
            pos+=FONTS[font].text_length(ch,fontsize=size)+tracking*size
    else:
        p.insert_text((x,y+size),s,fontsize=size,fontname=font,color=rgb(color))
    text_bounds.append((len(doc),s,x,y,width,size))
    return y+size


def para(p,s,x,y,w,size=10.5,leading=15.5,color=CHAR,font='body'):
    for block in s.split('\n'):
        words=block.split(); row=''
        for word in words:
            candidate=(row+' '+word).strip()
            if row and FONTS[font].text_length(candidate,fontsize=size)>w:
                txt(p,row,x,y,size,font,color);y+=leading;row=word
            else:row=candidate
        if row:txt(p,row,x,y,size,font,color);y+=leading
        y+=leading*.28
    return y


def label(p,s,x,y,color=BROWN):return txt(p,s.upper(),x,y,8,'semi',color,.09)


def heading(p,lines,x=42,y=91,size=27,color=BROWN):
    for s in lines.split('\n'):
        txt(p,s.upper(),x,y,size,'tenor',color,.08);y+=size*1.27
    return y


def image(p,path,x,y,w,h,cover=False):
    if not cover:
        p.insert_image(fitz.Rect(x,y,x+w,y+h),filename=str(path),keep_proportion=True)
    else:
        # Clip through a source PDF, preserving original photo pixels without destructive resampling.
        im=Image.open(path); iw,ih=im.size
        temp=fitz.open(); q=temp.new_page(width=iw,height=ih);q.insert_image(q.rect,filename=str(path))
        ratio=w/h
        if iw/ih>ratio:
            cw=ih*ratio;clip=fitz.Rect((iw-cw)/2,0,(iw+cw)/2,ih)
        else:
            ch=iw/ratio;clip=fitz.Rect(0,(ih-ch)/2,iw,(ih+ch)/2)
        p.show_pdf_page(fitz.Rect(x,y,x+w,y+h),temp,0,clip=clip)


def svg(p,name,x,y,w,h):
    s=fitz.open(E/(name+'.svg'));v=fitz.open('pdf',s.convert_to_pdf())
    p.show_pdf_page(fitz.Rect(x,y,x+w,y+h),v,0)


def logo(p,x,y,w,holding=False):
    h=w*357/373
    # Visible bird height in the supplied PNG is 124 px; outer file-edge clearance is conservative.
    unit=w*124/373
    if holding:rect(p,x-unit,y-unit,w+2*unit,h+2*unit,LINEN,r=.12)
    image(p,LOGO,x,y,w,h)
    return h,unit


def new(section,title):
    p=doc.new_page(width=W,height=H);rect(p,0,0,W,H,LINEN)
    label(p,'Papua Diving Resorts',42,29)
    txt(p,'BRAND GUIDELINES / 2026',375,30,8,'medium',BROWN)
    line(p,42,54,W-42,54)
    label(p,section,42,70)
    page_titles.append(title)
    line(p,42,796,W-42,796)
    txt(p,'RAJA AMPAT / SOUTHWEST PAPUA',42,807,7.5,'medium',BROWN,.05)
    txt(p,f'{len(doc):02d}',530,805,10,'tenor',BROWN)
    return p


def card(p,title,body,x,y,w=240):
    line(p,x,y,x+w,y,CLAY,1)
    txt(p,title,x,y+14,13,'semi',BROWN)
    return para(p,body,x,y+40,w)


def build_pdf(names):
    p=new('Identity manual','Rooted in place')
    image(p,A/'aug21_p01_img1.jpeg',42,82,511,410,True)
    logo(p,75,115,91,True)
    label(p,'One master brand. Two island experiences.',42,520)
    heading(p,'ROOTED IN PLACE.\nDRAWN TO THE REEF.',42,549,28)
    para(p,'Papua Diving Resorts\nBrand guidelines 2026',42,645,330,14,20)
    svg(p,names[0],42,725,511,45)

    p=new('01 / The brand','A shared sense of purpose')
    heading(p,'A SHARED SENSE\nOF PURPOSE.')
    para(p,'A place-led identity for two intimate island stays. Papuan heritage, reef knowledge and responsible hospitality shape the system.',42,180,490,13,19)
    card(p,'Vision','A future where Raja Ampat\'s people, culture and marine ecosystems thrive together through responsible tourism.',42,260)
    card(p,'Mission','Create environmentally responsible holidays, invest in local people and support lasting care for the marine environment.',313,260)
    for y,n,t,b in [(402,'01','Papuan knowledge','Credit the people, places and living traditions behind the experience.'),(483,'02','Conservation with evidence','Tell specific stories of stewardship. Verify claims before publication.'),(564,'03','Warm, informed hospitality','Help guests understand the place, from their first enquiry to their last dive.')]:
        txt(p,n,42,y,26,'tenor',CLAY);txt(p,t,104,y+2,15,'semi',BROWN);para(p,b,104,y+30,440)
    label(p,'Inside the manual',42,686)
    para(p,'03-05 Logo  /  06-08 Colour  /  09-10 Typography\n11 Voice  /  12 Imagery  /  13-14 Motifs  /  15-17 Applications\n18 Release checklist  /  19 Files & sources',42,711,510,10,16)

    p=new('02 / Logo system','The master stays unchanged')
    heading(p,'THE MASTER\nSTAYS UNCHANGED.')
    rect(p,42,192,511,325,CORAL)
    logo(p,222,248,150)
    label(p,'Supplied master / original pixels retained',145,480)
    card(p,'One identity','Use the supplied Papua Diving Resorts logo exactly as provided. Its bird, lettering, colour and proportions are fixed.',42,552)
    card(p,'Two resort descriptors','Set Sorido Bay Resort or Kri Eco Resort in Tenor Sans, outside the logo clear space. Do not build new lockups or separate resort logos.',313,552)
    para(p,'African lettering belongs only to the existing logo. Never retype, trace, simplify, outline, stretch, rotate, recolour or add effects to the mark.',42,704,511)

    p=new('02 / Logo system','Space gives the mark authority')
    heading(p,'SPACE GIVES THE\nMARK AUTHORITY.')
    x,y,w=211,260,150;h,u=logo(p,x,y,w)
    p.draw_rect(fitz.Rect(x-u,y-u,x+w+u,y+h+u),color=rgb(CLAY),width=.9,dashes='[4 3] 0')
    line(p,x-u,y-15,x,y-15,CLAY);label(p,'1x',x-u+15,y-34)
    line(p,x+w+17,y,x+w+17,y+u,CLAY);label(p,'1x',x+w+24,y+15)
    label(p,'x = height of the bird',42,190)
    para(p,'Measure the bird from its highest to lowest visible point. Reserve at least 1x on all four sides. Nothing enters this area: text, pattern, imagery detail or trim.',42,481,511)
    line(p,42,553,553,553)
    logo(p,70,588,32*72/25.4)
    txt(p,'32 mm',198,592,26,'tenor',BROWN)
    para(p,'Minimum print width\nMeasure at actual output size.',198,630,300)
    txt(p,'120 px',70,715,23,'tenor',BROWN)
    para(p,'Minimum digital display width. Use a 2x source for high-density screens; never shrink the mark to a favicon.',245,709,300)

    p=new('02 / Logo system','Protect the logo on dark fields')
    heading(p,'PROTECT THE LOGO\nON DARK FIELDS.')
    rect(p,42,190,246,275,BROWN);image(p,A/'aug21_p01_img1.jpeg',307,190,246,275,True)
    logo(p,116,267,98,True);logo(p,381,267,98,True)
    label(p,'Dark Papua Brown',42,483);label(p,'Dark / busy photography',307,483)
    para(p,'Use a Natural Linen #F6F1EB pill or rounded-rectangle holding shape. Keep the full 1x bird-height clear space inside the shape. Do not reverse or recolour the logo.',42,520,511,12,18)
    card(p,'Keep the supplied white field','The supplied raster has an opaque white background. It remains intact within the Linen holding shape; do not remove it or simulate a transparent master.',42,620)
    card(p,'Never improvise','No white reverse mark, drop shadow, tint, reduced opacity or unapproved crop. A future transparent/vector master must come from the brand owner.',313,620)

    p=new('03 / Colour','From bark to brand')
    heading(p,'FROM BARK\nTO BRAND.')
    para(p,'Eight shared earth tones. One restrained resort accent. Photography carries the sea; the identity stays grounded in bark, sand and linen.',42,180,500)
    for i,(n,h,c,role) in enumerate(PALETTE[:8]):
        col=i%2; row=i//2;x=42+col*267;y=250+row*125
        rect(p,x,y,52,93,h)
        txt(p,n,x+65,y+1,13,'semi',BROWN)
        txt(p,h,x+65,y+24,10,'medium')
        vals=tuple(round(v*255) for v in rgb(h))
        txt(p,'RGB '+', '.join(map(str,vals)),x+65,y+42,9)
        txt(p,'CMYK '+', '.join(map(str,c)),x+65,y+58,9)
        para(p,role,x+65,y+76,182,8.8,12)

    p=new('03 / Colour','One family, two expressions')
    heading(p,'ONE FAMILY.\nTWO EXPRESSIONS.')
    for x,title,subtitle,cs in [(42,'SORIDO BAY','Upscale boutique comfort',[LINEN,BROWN,TEAL]),(309,'KRI ECO','Authentic overwater eco-pioneer',[SAND,CLAY,SAGO])]:
        heading(p,title,x,205,19)
        para(p,subtitle,x,245,244,11,16)
        for j,c in enumerate(cs):rect(p,x+j*81.3,290,81.3,115,c)
        for j,c in enumerate(cs):txt(p,c,x,425+j*23,11,'medium',BROWN)
    line(p,42,520,553,520)
    label(p,'Sorido-only accent',42,542)
    rect(p,42,580,105,105,TEAL)
    txt(p,'Lagoon Reef Teal',172,577,20,'tenor',BROWN)
    para(p,'#1A5E63  /  RGB 26, 94, 99\nCMYK 85, 34, 42, 18\nUse in fine rules, small details and selected Sorido panels. It is not a new master-brand blue.',172,616,375)
    para(p,'Differentiate through palette emphasis, imagery and language. Keep the same logo, type families, spacing and graphic construction across both resorts.',42,726,511)

    p=new('03 / Colour','Colour with a clear role')
    heading(p,'COLOUR WITH\nA CLEAR ROLE.')
    label(p,'Recommended starting balance / excluding photography',42,185)
    start=42
    for fraction,c in [(.65,LINEN),(.2,BROWN),(.1,CLAY),(.05,SAGO)]:
        rect(p,start,220,511*fraction,70,c,stroke=SAND);start+=511*fraction
    para(p,'65% light neutrals  /  20% dark structure\n10% clay or ochre  /  5% resort or conservation accent',42,312,511,12,18)
    label(p,'Digital text pairings / calculated sRGB contrast',42,386)
    for i,(fg,bg,n) in enumerate([(CHAR,LINEN,'Body copy'),(BROWN,LINEN,'Headlines'),(LINEN,BROWN,'Dark panels'),(LINEN,TEAL,'Sorido panels'),(CHAR,SAGO,'Eco detail'),(LINEN,CLAY,'Warm CTA')]):
        x=42+(i%2)*267;y=420+(i//2)*79
        rect(p,x,y,244,60,bg)
        txt(p,n,x+12,y+9,12,'semi',fg)
        txt(p,f'{contrast(fg,bg):.2f}:1 contrast',x+12,y+32,9,'body',fg)
    para(p,'Use at least 4.5:1 for normal text and 3:1 for large text. Never set pale text on Ochre, Sandstone or Sago. Do not rely on colour alone to communicate meaning.',42,682,511)
    para(p,'Print: supplied CMYK values are specification targets, not an ICC conversion. Agree the stock and output profile with the printer; approve a physical proof.',42,744,511,9,13)

    p=new('04 / Typography','A quieter, clearer voice')
    heading(p,'A QUIETER,\nCLEARER VOICE.')
    label(p,'Display / Tenor Sans Regular',42,187)
    heading(p,'DIVE DEEPER.\nSTAY CLOSER.',42,224,32)
    para(p,'ABCDEFGHIJKLMNOPQRSTUVWXYZ\nabcdefghijklmnopqrstuvwxyz 0123456789',42,328,500,15,22,font='tenor')
    line(p,42,407,553,407)
    label(p,'Body / Source Sans 3 Regular',42,429)
    para(p,'On Kri Island, days move between warm water, generous reefs and quiet evenings. A stay with Papua Diving connects the experience of the reef with the people who know it.',42,468,355,10.5,15.5)
    txt(p,'Aa',438,467,65,'body',CLAY)
    label(p,'Subheads / Source Sans 3 SemiBold',42,578)
    txt(p,'Local knowledge. Shared discovery.',42,617,20,'semi',BROWN)
    label(p,'Navigation / Source Sans 3 Medium',42,674)
    txt(p,'STAY     DIVING     CONSERVATION     JOURNAL',42,711,12,'medium',BROWN,.04)
    para(p,'Replace Karla in new material. Keep African lettering exclusive to the supplied logo.',42,756,511,9,13)

    p=new('04 / Typography','Hierarchy that travels well')
    heading(p,'HIERARCHY THAT\nTRAVELS WELL.')
    rows=[('H1 / hero','Tenor Sans Regular','30 / 38 pt','48 / 60 px','UPPERCASE / +0.08em'),('H2 / resort title','Tenor Sans Regular','22 / 28 pt','32 / 40 px','UPPERCASE / +0.08em'),('H3 / subheading','Source Sans 3 SemiBold','14 / 19 pt','22 / 29 px','Sentence case / normal'),('Navigation','Source Sans 3 Medium','10 / 14 pt','16 / 22 px','Short, descriptive labels'),('Body / editorial','Source Sans 3 Regular','10.5 / 15.5 pt','16 px / 1.65','Sentence case / normal'),('Caption / utility','Source Sans 3 Regular','8.5 / 12 pt','13 / 18 px','Keep meaning readable')]
    for i,(n,f,pr,we,r) in enumerate(rows):
        y=191+i*79;line(p,42,y,553,y);txt(p,n,42,y+10,12,'semi',BROWN)
        txt(p,f,42,y+32,9);txt(p,'PRINT  '+pr,310,y+11,10,'medium');txt(p,'WEB    '+we,310,y+32,10,'medium');txt(p,r,42,y+53,9,'body',CLAY)
    para(p,'Use left-aligned body text with a comfortable 45-75 characters per line. Never track body copy. Leave at least one body line between paragraphs and 1.5 lines before a new subheading.',42,692,511)
    para(p,'For narrow screens: H1 may reduce to 32/40 px. Keep body text at 16 px and preserve hierarchy. Do not stretch text to fit a measure.',42,754,511,9,13)

    p=new('05 / Voice & tone','Warm, informed, specific')
    heading(p,'WARM. INFORMED.\nSPECIFIC.')
    para(p,'Speak as a thoughtful host who knows the place. Invite discovery, share useful knowledge and give conservation claims context.',42,181,490,13,19)
    examples=[('Invite, do not oversell','Explore Raja Ampat with the people who know its reefs.','The ultimate untouched paradise.'),('Make responsibility tangible','Meet the guides and learn how to care for the reef during your stay.','The world\'s most sustainable resort.'),('Respect living culture','Papuan people, knowledge and traditions are part of the story.','Exotic tribes and primitive island life.')]
    for i,(t,yes,no) in enumerate(examples):
        y=280+i*137;label(p,t,42,y);txt(p,'SAY',42,y+30,9,'semi',BROWN);para(p,yes,96,y+26,450,12,17);txt(p,'AVOID',42,y+82,9,'semi',CLAY);para(p,no,96,y+78,450,10.5,15.5)
    line(p,42,712,553,712)
    para(p,'Sorido Bay: calm, attentive, refined. Kri Eco: direct, resourceful, close to nature. Both: welcoming, educational and rooted in place. Check names, figures, awards and environmental claims before release.',42,733,511,10,14)

    p=new('06 / Imagery','Let the place lead')
    heading(p,'LET THE\nPLACE LEAD.')
    image(p,A/'aug21_p01_img1.jpeg',42,190,280,300,True)
    image(p,A/'aug21_p06_img1.jpeg',337,190,216,144,True)
    image(p,A/'brief_p4_img1.jpeg',337,349,216,141,True)
    label(p,'Landscape / reef / lived experience',42,511)
    card(p,'Choose','Real Raja Ampat landscapes, reef biodiversity, local guides, guests and natural materials. Preserve honest water colour and natural skin tones. Credit photographers and confirm usage rights.',42,551)
    card(p,'Compose','Give the subject space. Keep a quiet area for type; use a Linen field when contrast is uncertain. Protect the logo with its holding shape. Crop responsively without losing the subject.',313,551)
    para(p,'Avoid fabricated destination scenes, generic tropical stock, heavy cyan saturation and decorative cultural imagery without context or consent. Source photography in this manual comes from the supplied employer PDFs.',42,722,511,10,15)

    p=new('07 / Graphic language','Bark first, reef second')
    heading(p,'BARK FIRST.\nREEF SECOND.')
    for i,n in enumerate(['brief_p3_img1.jpeg','brief_p3_img2.jpeg','brief_p3_img3.jpeg']):image(p,A/n,42+i*175,188,161,214,True)
    label(p,'Supplied bark-painting references / brief page 3',42,418)
    para(p,'The reference paintings use repeated bands, directional geometry, nested shapes and earth pigments. Translate that rhythm into restrained borders, rather than copying figurative or potentially sacred forms.',42,455,511,12,18)
    svg(p,names[0],42,550,511,69)
    card(p,'A new graphic interpretation','These assets are original bark-inspired geometry, not authenticated traditional artworks. The wave divider describes reef currents; it has no claimed traditional meaning.',42,647)
    card(p,'Cultural integrity','Reference the supplied interior and cultural imagery on brief page 4 with respect. Have Papuan artists or culture-holders review new motifs before commercial production.',313,647)

    p=new('07 / Graphic language','Three assets, one rhythm')
    heading(p,'THREE ASSETS.\nONE RHYTHM.')
    label(p,'01 / Papuan Bark Chevron Border',42,184);svg(p,names[0],42,218,511,68)
    para(p,'Primary border for page edges, sleeves and packaging. Repeat horizontally at its native tile width; keep the aspect ratio. Never run a motif through logo clear space.',42,308,511)
    label(p,'02 / Raja Ampat Current Wave Divider',42,387);svg(p,names[1],42,422,511,55)
    para(p,'Secondary divider for editorial and digital sections. Keep it quieter than the bark border. Avoid stacking both motifs in one small field.',42,501,511)
    label(p,'03 / Sorido Kri Corner Emblem',42,579);svg(p,names[2],42,615,128,128)
    para(p,'A shared decorative corner for a menu, card or presentation. Rotate by 90 degrees to suit the corner. Never use it as a resort logo or badge of cultural authenticity.',201,619,352)
    para(p,'SVG: scalable vector, transparent background.\nPNG: 4800 x 640 / 4800 x 520 / 1200 x 1200 px, transparent, 300 ppi metadata. Use at intended size; proof fine lines on fabric.',201,706,352,9,13)

    p=new('08 / Applications','The editorial invitation')
    heading(p,'THE EDITORIAL\nINVITATION.')
    rect(p,42,183,330,570,CORAL)
    image(p,A/'aug21_p01_img1.jpeg',54,195,306,280,True)
    logo(p,77,220,57,True)
    heading(p,'DIVE DEEPER.\nSTAY CLOSER.',61,501,20)
    para(p,'Two island experiences. One shared commitment to Raja Ampat.',61,566,289,11,16)
    para(p,'Discover Sorido Bay Resort and Kri Eco Resort, where reef exploration meets warm, place-led hospitality.',61,614,279)
    txt(p,'papua-diving.com',61,691,12,'semi',BROWN)
    svg(p,names[0],54,724,306,22)
    label(p,'Print advert',395,194)
    para(p,'Lead with one real image and one short headline. Keep body copy concise. End with one clear destination.',395,226,157)
    label(p,'Layout rules',395,370)
    para(p,'Use 12-15 mm margins. Keep logo clearance. Preserve a calm reading measure. Motif remains an edge detail.',395,402,157)
    label(p,'Production',395,552)
    para(p,'Add bleed only in the final advert file. Check image resolution at final size. Confirm all marketing copy before release.',395,584,157)
    txt(p,'Scaled application study / not a press advert file',42,768,8,'body',CLAY)

    p=new('08 / Applications / reduced studies','From screen to stay')
    heading(p,'FROM SCREEN\nTO STAY.')
    # Website specimen, rendered as live vector layout in the PDF.
    rect(p,42,187,511,280,CORAL)
    logo(p,61,205,40)
    txt(p,'STAY     DIVING     CONSERVATION',203,224,9,'medium',BROWN)
    image(p,A/'aug21_p06_img1.jpeg',300,271,235,177,True)
    heading(p,'ROOTED IN\nRAJA AMPAT.',59,290,18)
    para(p,'Two intimate island stays, connected by a love of the reef.',59,358,208,10,15)
    rect(p,59,412,146,27,BROWN);txt(p,'Explore the resorts',72,418,10,'semi',LINEN)
    label(p,'Website / adapt the layout, keep the hierarchy',42,486)
    rect(p,42,535,244,201,SAND);rect(p,309,535,244,201,TEAL)
    heading(p,'KRI ECO',57,557,20);para(p,'A closer rhythm\nwith island life.',57,604,213,14,20)
    svg(p,names[0],57,690,213,28)
    heading(p,'SORIDO BAY',324,557,18,LINEN);para(p,'A quieter base\nfor reef discovery.',324,604,213,14,20,LINEN)
    para(p,'Reduced studies: retain 32 mm / 120 px logo minimums at final output. Social tiles use one readable message; resort titles are descriptors, never substitute logos.',42,755,511,9,13)

    p=new('08 / Applications / reduced studies','Small details, shared identity')
    heading(p,'SMALL DETAILS.\nSHARED IDENTITY.')
    label(p,'Guest card / stationery',42,186)
    rect(p,42,216,310,196,SAND)
    logo(p,68,242,67)
    txt(p,'WELCOME TO',171,253,9,'semi',BROWN,.06)
    heading(p,'KRI ECO',171,278,16)
    para(p,'Your island stay\nbegins here.',171,316,157,11,16)
    svg(p,names[0],54,380,286,23)
    para(p,'Warm stock. Clear hierarchy. One narrow border. Keep practical guest information direct and readable.',376,231,177)
    label(p,'Email signature / editable text',42,453)
    line(p,42,487,553,487)
    logo(p,57,513,63)
    txt(p,'Guest Relations',158,514,14,'semi',BROWN)
    txt(p,'Papua Diving Resorts',158,541,11,'body')
    txt(p,'Sorido Bay Resort / Kri Eco Resort',158,563,10,'body')
    txt(p,'papua-diving.com',158,585,10,'medium',BROWN)
    card(p,'Presentation & newsletter','Use a Linen field, a short Tenor title and generous photo space. For email clients without brand fonts, use Arial for live text; never turn a whole message into an image.',42,649)
    card(p,'Clothing & merchandise','Keep the logo unchanged. Add bark detail at one cuff, hem or edge. Use a Linen holding patch on dark fabric. Request embroidery and print samples before manufacture.',313,649)

    p=new('09 / Everyday checks','Consistency is a practice')
    heading(p,'CONSISTENCY\nIS A PRACTICE.')
    for i,(t,yes,no) in enumerate([
        ('Logo','Keep the supplied master, 1x clearance and minimum sizes.','Recolour, stretch, redraw, reverse or crowd the mark.'),
        ('Colour','Use the specified master colours and resort emphasis.','Add new blues, overuse accents or guess print conversions.'),
        ('Type','Use Tenor + Source Sans 3 with the stated hierarchy.','Bring back Karla, fake bold Tenor or use African as body text.'),
        ('Image','Choose real imagery with permission and natural colour.','Invent destination scenes or publish unsupported claims.'),
        ('Pattern','Use one quiet accent and preserve its proportions.','Call unreviewed motifs authentic or assign invented meanings.')]):
        y=191+i*104;line(p,42,y,553,y);label(p,t,42,y+11);para(p,'DO  '+yes,150,y+8,401,10.5,15.5);para(p,'AVOID  '+no,150,y+47,401,10,14,CLAY)
    rect(p,42,730,511,44,BROWN)
    txt(p,'Before release: check copy, rights, contrast, size and proof.',57,743,11,'semi',LINEN)

    p=new('10 / Delivery & provenance','Built to be used')
    heading(p,'BUILT TO\nBE USED.')
    label(p,'The supplied brand kit',42,186)
    para(p,'Printable A4 PDF with embedded fonts and vector motifs\nASE colour library + exact RGB / CMYK reference sheet\nThree scalable SVGs + three transparent PNGs\nUnmodified cropped logo + font files and OFL licences\nREADME with usage, production notes and file checksums',42,220,511,12,22)
    label(p,'Source hierarchy',42,365)
    para(p,'This 2026 system follows the current production specification: 1x bird-height logo clearance, 32 mm / 120 px minimum widths, Linen holding shapes and Tenor Sans + Source Sans 3. Earlier exploratory font and logo rules are superseded here.',42,396,511)
    label(p,'Employer source documents',42,493)
    for i,s in enumerate(['Brand Guidelines Brief 2026 (18 pages)','(AUG12) Papua Diving Revised Brand Guidelines (12 pages)','(AUG19) Brand Applications Mockup Compendium (11 pages)','(AUG 21) Typography Body Copy Comparison (7 pages)']):txt(p,s,42,524+i*23,10,'body')
    label(p,'Print & cultural production notes',42,641)
    para(p,'This is an A4 reference book, not a PDF/X press separation. Text and motifs remain vector; source photographs and the logo retain their supplied resolution. Request original high-resolution photography and an approved vector logo for large-format work. Match CMYK to stock with a printer proof. Review new bark-inspired artwork with Papuan collaborators before commercial production.',42,673,511,10.5,15.5)

    doc.set_metadata({'title':'Papua Diving Resorts - Brand Guidelines 2026','author':'Papua Diving Resorts','subject':'Master identity, Sorido Bay Resort and Kri Eco Resort','keywords':'brand guidelines, Southwest Papua, Raja Ampat, 2026'})
    doc.set_toc([[1,f'{i:02d}  {title}',i] for i,title in enumerate(page_titles,1)])
    doc.subset_fonts()
    doc.save(E/PDF_NAME,garbage=4,deflate=True)
    return len(doc)


def render_previews():
    pdf=fitz.open(E/PDF_NAME)
    previews=E/'previews';previews.mkdir(exist_ok=True)
    thumbs=[]
    for i,p in enumerate(pdf):
        p.get_pixmap(matrix=fitz.Matrix(1.6,1.6)).save(previews/f'page-{i+1:02d}.png')
        im=Image.open(previews/f'page-{i+1:02d}.png').convert('RGB');im.thumbnail((238,337))
        tile=Image.new('RGB',(258,369),'#e1d6c7');tile.paste(im,((258-im.width)//2,8));ImageDraw.Draw(tile).text((12,349),f'{i+1:02d}  {page_titles[i][:28]}',fill='#342b24');thumbs.append(tile)
    sheet=Image.new('RGB',(258*5,369*math.ceil(len(thumbs)/5)),'#e1d6c7')
    for i,im in enumerate(thumbs):sheet.paste(im,((i%5)*258,(i//5)*369))
    sheet.save(T/'book-contact.jpg')


def build_boards(names):
    css='''@font-face{font-family:Tenor;src:url('assets/fonts/TenorSans-Regular.ttf')}@font-face{font-family:Source;src:url('assets/fonts/SourceSans3-Regular.ttf');font-weight:400}@font-face{font-family:Source;src:url('assets/fonts/SourceSans3-SemiBold.ttf');font-weight:600}@font-face{font-family:Source;src:url('assets/fonts/SourceSans3-Medium.ttf');font-weight:500}*{box-sizing:border-box}body{margin:0;background:#F6F1EB;color:#2B2A27;font-family:Source,sans-serif}.board{width:1600px;height:1200px;position:relative;overflow:hidden;padding:56px 64px}header{display:flex;justify-content:space-between;border-bottom:1px solid #DCCAAF;padding-bottom:20px;font-size:17px;letter-spacing:.12em;color:#7E2F19}h1,h2,h3{font-family:Tenor,sans-serif;font-weight:400;color:#7E2F19;text-transform:uppercase;letter-spacing:.08em;margin:0}h1{font-size:52px;line-height:1.2}h2{font-size:32px;line-height:1.3}h3{font-size:23px}p{font-size:21px;line-height:1.55;margin:16px 0}.kicker{font-size:16px;letter-spacing:.12em;text-transform:uppercase;font-weight:600;color:#A65A2A}.small{font-size:17px;line-height:1.5}.footer{position:absolute;bottom:30px;left:64px;right:64px;display:flex;justify-content:space-between;border-top:1px solid #DCCAAF;padding-top:14px;font-size:14px;color:#7E2F19;letter-spacing:.08em}.pill{background:#F6F1EB;border-radius:24px;padding:calc(var(--logo-w)*.33244);display:inline-flex;align-items:center;justify-content:center}.pill img{width:var(--logo-w);height:auto;display:block}.rule{height:1px;background:#DCCAAF;margin:24px 0}.photo{object-fit:cover}.swatches{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}.swatch .chip{height:74px}.swatch strong{font-size:18px;display:block;margin-top:9px}.swatch span{display:block;font-size:15px;line-height:1.45}.row{display:flex;gap:32px}a{color:inherit;text-underline-offset:4px}a:hover{color:#A65A2A}a:active{color:#7E2F19}a:focus-visible{outline:3px solid #1A5E63;outline-offset:5px}.board-four .rule{margin:18px 0}.board-four .small{font-size:16px}.page{box-shadow:0 12px 30px #2b2a2720;border:1px solid #DCCAAF}.serif{font-family:Tenor;letter-spacing:.08em;text-transform:uppercase}.split{display:grid;grid-template-columns:1fr 1fr;gap:56px}@media print{@page{size:1600px 1200px;margin:0}body{-webkit-print-color-adjust:exact;print-color-adjust:exact}}'''
    (ROOT/'boards-codex.css').write_text(css)
    footer=lambda n:f'<footer class="footer"><span>PAPUA DIVING RESORTS / BRAND GUIDELINES 2026</span><span>RAJA AMPAT · SOUTHWEST PAPUA</span><span>0{n} / 04</span></footer>'
    head=lambda s:f'<header><span>PAPUA DIVING RESORTS</span><span>{s}</span><span>IDENTITY / 2026</span></header>'
    pill=lambda w:f'<div class="pill" style="--logo-w:{w}px"><img src="assets/papua_logo_cropped.png" alt="Unchanged Papua Diving Resorts logo"></div>'
    # Hero image occupies 72% of this presentation board; source is employer photography.
    b1=f'''<div class="board" style="padding:0"><img class="photo" src="assets/aug21_p01_img1.jpeg" alt="Forested Raja Ampat coastline and reef from the supplied imagery" style="position:absolute;inset:0;width:1150px;height:1200px;object-position:53% center"><div style="position:absolute;left:96px;top:92px">{pill(150)}</div><section style="position:absolute;left:1088px;top:0;width:512px;height:1200px;padding:72px 46px;background:#F6F1EB"><p class="kicker">A sense of place / 2026</p><h1 style="margin-top:84px;font-size:48px">ROOTED<br>IN PLACE.<br><br>DRAWN<br>TO THE<br>REEF.</h1><p style="margin-top:34px">One enduring identity.<br>Two island experiences.</p><div class="rule"></div><p class="small">SORIDO BAY RESORT<br>KRI ECO RESORT</p><img src="exports/{names[0]}.svg" alt="Bark-inspired chevron border" style="width:400px;height:65px;object-fit:contain;margin-top:36px"><p class="small" style="margin-top:34px">Brand guidelines · {len(doc)} pages<br>Logo / Colour / Type / Motifs</p><a class="small" href="exports/{PDF_NAME}">Open the complete guidelines ↗</a><p class="kicker" style="position:absolute;bottom:35px">01 / 04</p></section></div>'''
    sw=''.join(f'<div class="swatch"><div class="chip" style="background:{h}"></div><strong>{n}</strong><span>{h} · RGB {", ".join(str(round(v*255)) for v in rgb(h))}</span><span>CMYK {", ".join(map(str,c))}</span></div>' for n,h,c,r in PALETTE)
    b2=f'''<div class="board">{head('THE IDENTITY TOOLKIT')}<div style="margin-top:40px"><p class="kicker">01 / Preserve the heritage</p><h1>THE MARK STAYS. THE SYSTEM CLARIFIES.</h1></div><div style="display:grid;grid-template-columns:630px 1fr;gap:64px;margin-top:38px"><section><div style="height:397px;background:#EFE5D6;display:flex;align-items:center;justify-content:center"><div style="padding:63px;border:1px dashed #A65A2A;position:relative"><img src="assets/papua_logo_cropped.png" alt="Master logo with one bird-height clear space" style="width:190px;display:block"><span style="position:absolute;top:18px;left:18px;font-size:20px">1x</span></div></div><div class="row" style="margin-top:24px"><div style="flex:1"><h2>1x</h2><p class="small">Bird-height clear space<br>on every side.</p></div><div style="flex:1"><h2>32 mm</h2><p class="small">Minimum print width.<br>120 px minimum digital.</p></div></div><div class="row" style="height:215px;margin-top:16px"><div style="background:#7E2F19;flex:1;display:grid;place-items:center">{pill(120)}</div><div style="background:url('assets/aug21_p01_img1.jpeg') center/cover;flex:1;display:grid;place-items:center">{pill(120)}</div></div><p class="small">Dark backgrounds: Natural Linen holding shape.<br>No recolouring. No stretching. Original white raster field retained.</p></section><section><p class="kicker" style="margin-top:0">02 / Bark, sand, linen & reef</p><div class="swatches">{sw}</div><div class="rule"></div><p class="small"><strong>One shared palette.</strong> Earth tones lead. Lagoon Reef Teal is reserved for Sorido Bay accents; blue comes primarily from photography.</p><p class="small">CMYK values follow the supplied specification.<br>Match the paper and press through a physical proof.</p></section></div>{footer(2)}</div>'''
    b3=f'''<div class="board">{head('TYPOGRAPHY & RESORT EXPRESSION')}<div style="margin-top:40px"><p class="kicker">03 / A clearer editorial voice</p><h1>ONE VOICE. TWO WAYS TO STAY.</h1></div><div class="split" style="margin-top:44px"><section><p class="kicker">Tenor Sans / Regular</p><h2 style="font-size:55px;line-height:1.25;margin-top:25px">DIVE DEEPER.<br>STAY CLOSER.</h2><p class="small">H1, H2 & resort names / UPPERCASE / +0.08em</p><div class="rule"></div><p class="kicker">Source Sans 3 / Regular</p><p style="font-size:25px;line-height:1.65;max-width:630px">On Kri Island, days move between warm water, generous reefs and quiet evenings. A stay connects the experience of the reef with the people who know it.</p><p class="small">Print: 10.5pt / 15.5pt · Web: 16px / 1.65</p><div class="rule"></div><p style="font-size:23px;font-weight:600">Local knowledge. Shared discovery.</p><p class="small">Subheadings: Source Sans 3 SemiBold<br>Navigation: Source Sans 3 Medium</p><p style="font-weight:500;font-size:19px;margin-top:28px">STAY &nbsp; DIVING &nbsp; CONSERVATION &nbsp; JOURNAL</p><p class="small" style="margin-top:38px">Karla is replaced in new material.<br>African lettering stays exclusive to the approved logo.</p></section><section><article style="padding:30px;background:#7E2F19;color:#F6F1EB;height:386px"><p class="kicker" style="color:#DCCAAF">Upscale boutique comfort</p><h2 style="color:#F6F1EB;margin-top:22px">SORIDO BAY RESORT</h2><p>Refined. Intimate. Unhurried.</p><div style="display:flex;height:67px;margin-top:40px"><div style="background:#F6F1EB;flex:1"></div><div style="background:#7E2F19;flex:1;border:1px solid #DCCAAF"></div><div style="background:#1A5E63;flex:1"></div></div><p class="small">Natural Linen + Papua Brown + Lagoon Reef Teal</p></article><article style="padding:30px;background:#DCCAAF;margin-top:25px;height:386px"><p class="kicker" style="color:#7E2F19">Authentic overwater eco-pioneer</p><h2 style="margin-top:22px">KRI ECO RESORT</h2><p>Close to nature. Open to discovery.</p><div style="display:flex;height:67px;margin-top:40px"><div style="background:#DCCAAF;flex:1;border:1px solid #7E2F19"></div><div style="background:#A65A2A;flex:1"></div><div style="background:#A8B69A;flex:1"></div></div><p class="small">Sandstone + Bark Clay + Sago Leaf</p></article></section></div>{footer(3)}</div>'''
    b4=f'''<div class="board board-four">{head('GRAPHIC LANGUAGE & COMPLETE DELIVERY')}<div style="margin-top:40px"><p class="kicker">04 / A rhythm drawn from place</p><h1>BARK FIRST. REEF SECOND.</h1></div><div style="display:grid;grid-template-columns:650px 1fr;gap:64px;margin-top:38px"><section><p class="kicker">Papuan Bark Chevron Border</p><img src="exports/{names[0]}.svg" alt="Geometric bark chevrons" style="width:650px;height:110px;margin:16px 0"><p class="small">Primary border / scalable vector / transparent PNG</p><div class="rule"></div><p class="kicker">Raja Ampat Current Wave Divider</p><img src="exports/{names[1]}.svg" alt="Three flowing reef-current lines" style="width:650px;height:95px;margin:12px 0"><p class="small">Secondary editorial divider / continuous horizontal repeat</p><div class="rule"></div><div class="row"><img src="exports/{names[2]}.svg" alt="Nested corner ornament" style="width:175px;height:175px"><div><p class="kicker">Sorido Kri Corner Emblem</p><p class="small">Shared decorative corner.<br>Never a replacement logo.</p></div></div><div class="rule"></div><p class="small">Original bark-inspired geometry, informed by the employer's references. No sacred meaning or cultural authentication is claimed. Local cultural review precedes commercial production.</p></section><section><div class="row" style="gap:18px;align-items:flex-start"><img class="page" src="exports/previews/page-01.png" alt="Guidelines cover" style="width:320px"><img class="page" src="exports/previews/page-06.png" alt="Complete colour specification page" style="width:250px;margin-top:54px"></div><div style="margin-top:35px"><h2>THE COMPLETE BRAND KIT</h2><p>{len(doc)}-page A4 brand guidelines<br>ASE palette · 3 SVG + 3 transparent PNG<br>Unchanged logo · fonts & usage notes</p><p class="small">Embedded type. Vector graphic elements.<br>Exact colour specifications and practical application rules.</p><div class="rule"></div><p><a href="exports/{PDF_NAME}">Read the guidelines ↗</a><br><a href="exports/{ZIP_NAME}" download>Download the complete kit ↓</a></p></div></section></div>{footer(4)}</div>'''
    for i,body in enumerate([b1,b2,b3,b4],1):
        (ROOT/f'board{i}-codex.html').write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=1600,initial-scale=1"><title>Papua Diving Resorts / Board {i:02d}</title><link rel="stylesheet" href="boards-codex.css"></head><body>{body}</body></html>')


def ase_entries(path):
    data=path.read_bytes()
    if data[:4]!=b'ASEF':raise ValueError('Invalid ASE header')
    count=struct.unpack('>I',data[8:12])[0];pos=12;entries=[]
    for _ in range(count):
        typ,size=struct.unpack('>HI',data[pos:pos+6]);pos+=6;payload=data[pos:pos+size];pos+=size
        if typ!=1:continue
        chars=struct.unpack('>H',payload[:2])[0];name=payload[2:2+chars*2].decode('utf-16-be').rstrip('\0');off=2+chars*2;model=payload[off:off+4].decode('ascii');n={'RGB ':3,'CMYK':4,'LAB ':3,'Gray':1}[model];vals=struct.unpack('>'+str(n)+'f',payload[off+4:off+4+n*4]);entries.append({'name':name,'model':model,'values':vals})
    return entries


def build_palette():
    path=E/'Papua_Diving_Resorts_2026_Master_Palette.ase'
    backup=T/'Papua_Diving_Resorts_2026_Master_Palette.before.ase'
    if path.exists() and not backup.exists():
        shutil.copyfile(path,backup)
    def string(s):
        data=(s+'\0').encode('utf-16-be')
        return struct.pack('>H',len(data)//2)+data
    def block(t,data):return struct.pack('>HI',t,len(data))+data
    blocks=[]
    for group,model in [('2026 / sRGB','RGB '),('2026 / supplied CMYK targets','CMYK')]:
        blocks.append(block(0xc001,string(group)))
        for name,h,c,role in PALETTE:
            values=rgb(h) if model=='RGB ' else tuple(v/100 for v in c)
            body=string(name)+model.encode()+struct.pack('>'+str(len(values))+'f',*values)+struct.pack('>H',0)
            blocks.append(block(1,body))
        blocks.append(block(0xc002,b''))
    path.write_bytes(b'ASEF'+struct.pack('>HHI',1,0,len(blocks))+b''.join(blocks))


def package(names):
    shutil.copyfile(LOGO,E/LOGO.name)
    font_out=E/'fonts';font_out.mkdir(exist_ok=True)
    for n in list(FONT_FILES.values())+['TenorSans-OFL.txt','SourceSans3-OFL.txt']:shutil.copyfile(F/n,font_out/n)
    specs=[{'name':n,'hex':h,'rgb':[round(v*255) for v in rgb(h)],'cmyk':list(c),'role':r} for n,h,c,r in PALETTE]
    (E/'Colour_Specifications.json').write_text(json.dumps(specs,indent=2)+'\n')
    readme=f'''# Papua Diving Resorts / 2026 Brand Kit

## Contents
- {PDF_NAME}: {len(doc)}-page A4 printable reference book, embedded fonts and vector graphics.
- Papua_Diving_Resorts_2026_Master_Palette.ase: nine current colours in sRGB and supplied-CMYK groups (18 swatches).
- Colour_Specifications.json: authoritative numeric HEX, RGB and supplied CMYK targets, including Sorido Teal.
- Three SVG motifs: scalable, transparent backgrounds, no embedded raster images or text objects.
- Three PNG motifs: 4800 x 640, 4800 x 520 and 1200 x 1200 pixels, RGBA, 300 ppi metadata.
- papua_logo_cropped.png: original 373 x 357 supplied raster, unchanged (including its opaque white field).
- fonts/: Tenor Sans Regular; Source Sans 3 Regular, Medium, SemiBold; OFL licences.
- SHA256SUMS.txt: file integrity list.

## Use
Master logo clear space is at least one bird height on every side. Minimum widths: 32 mm print / 120 px digital.
On dark photography or dark brown, use the Natural Linen #F6F1EB rounded holding shape with the full clear space inside.
Do not recolour, stretch, reverse, trace, rebuild or remove the background from the supplied master.
SVG borders repeat horizontally at native aspect ratio. Keep all motifs outside logo clear space.
Motifs are new bark-inspired geometric designs, not culturally authenticated traditional artwork. Obtain local Papuan review before commercial production.

## Typography
Tenor Sans Regular headings: uppercase, +0.08em tracking.
Source Sans 3 SemiBold subheads; Medium navigation; Regular body.
Body: 10.5pt / 15.5pt print; 16px / 1.65 web. Karla is replaced in new work.
Fonts are from the Google Fonts official repository; Source Sans static weights were instantiated from its variable font.

## Print notes
The reference book is A4, 210 x 297 mm, with live embedded type and vector motifs. It has no bleed and is not PDF/X.
Colour fills in the reference PDF use sRGB. The exact supplied CMYK targets are printed in the manual and in JSON; they are not ICC-converted equivalents.
The ASE replaces the earlier exploratory blue/mist swatches with the specified Lagoon Reef Teal. Its RGB and CMYK groups follow Colour_Specifications.json exactly. The original ASE is backed up in tmp/pdfs in the working project.
Approve an output-profile/stock-specific physical colour proof. Use an approved vector logo for large-format production.
At 32 mm the original logo is approximately 296 ppi. Enlarged explanatory specimens and source PDF photography are limited by supplied pixel dimensions; no artificial detail was added.
The employer-supplied photography is used for reference layouts; confirm original high-resolution files and usage rights for commercial campaigns.

## Rebuild
At project root: `python3 build_guidelines_2801171.py`.
Uses existing PyMuPDF and Pillow. assets/fonts must contain the supplied local fonts.
Four 1600 x 1200 HTML boards and boards-codex.css are generated alongside the script. Boards use local assets and include working PDF/ZIP links.
'''
    (E/'README_Brand_Kit.md').write_text(readme)
    files=[E/PDF_NAME,E/'Papua_Diving_Resorts_2026_Master_Palette.ase',E/'Colour_Specifications.json',E/LOGO.name,E/'README_Brand_Kit.md']
    files += [E/(n+ext) for n in names for ext in ('.svg','.png')]+sorted(font_out.iterdir())
    (E/'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(E)}\n' for p in files))
    files.append(E/'SHA256SUMS.txt')
    with zipfile.ZipFile(E/ZIP_NAME,'w',zipfile.ZIP_DEFLATED) as z:
        for p in files:z.write(p,str(p.relative_to(E)))


def validate(names):
    assert hashlib.sha256(LOGO.read_bytes()).hexdigest()==LOGO_HASH
    assert (E/LOGO.name).read_bytes()==LOGO.read_bytes()
    with zipfile.ZipFile(E/ZIP_NAME) as z:assert z.testzip() is None
    for n in names:
        tree=ET.parse(E/f'{n}.svg');assert not any(e.tag.split('}')[-1] in ['text','image'] for e in tree.iter())
        im=Image.open(E/f'{n}.png');assert im.mode=='RGBA' and im.getextrema()[3][0]==0
    p=fitz.open(E/PDF_NAME);assert len(p)==19
    text='\n'.join(q.get_text() for q in p).replace('\xa0',' ')
    for s in ['120 px','32 mm','1x','10.5 / 15.5','16 px / 1.65','Tenor Sans','Source Sans 3']+[h for _,h,_,_ in PALETTE]:assert s in text,s
    for q in p:
        for b in q.get_text('dict')['blocks']:
            if b['type']!=0:continue
            x0,y0,x1,y1=b['bbox'];assert x0>=0 and y0>=0 and x1<=W+.1 and y1<=H+.1,(q.number,b)
        assert all(f[1]!='n/a' for f in q.get_fonts()),q.number
    entries=ase_entries(E/'Papua_Diving_Resorts_2026_Master_Palette.ase')
    assert len(entries)==18
    for n,h,c,role in PALETTE:
        for model,target in [('RGB ',rgb(h)),('CMYK',tuple(v/100 for v in c))]:
            entry=next(e for e in entries if e['name']==n and e['model']==model)
            assert all(abs(a-b)<1e-6 for a,b in zip(entry['values'],target))
    report={'pages':len(p),'page_size':'A4','logo_sha256':LOGO_HASH,'logo_unchanged':True,'zip_crc':'passed','motifs':names,'svg_raster_or_text_objects':0,'png_background':'transparent','fonts':'embedded','text_page_bounds':'passed','ase_entries':entries,'contrast':{f'{a} on {b}':round(contrast(a,b),3) for a,b in [(CHAR,LINEN),(BROWN,LINEN),(LINEN,BROWN),(LINEN,TEAL),(CHAR,SAGO),(LINEN,CLAY)]}}
    (E/'build-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='ase_entries'},indent=2))


if __name__=='__main__':
    build_palette()
    names=build_motifs()
    build_pdf(names)
    render_previews()
    build_boards(names)
    package(names)
    validate(names)

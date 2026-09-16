from pathlib import Path
import json,html,re
root=Path(__file__).resolve().parent.parent;site=root;public=site/'public'
assets=json.loads((root/'source/assets.json').read_text(encoding='utf-8'))
videos=json.loads((root/'source/videos.json').read_text())
assert len(videos)==5
E=html.escape
projects=[
 {'id':'healing-center','number':'01','section':'Exterior','title':'Cancer Healing Center','type':'Graduation project · Healthcare','heading':'Architecture around the healing landscape.','body':'Low-rise volumes frame gardens and courtyards, bringing nature into the everyday experience of care. Shaded routes, planted edges and sheltered outdoor spaces connect the buildings and give the project its rhythm.','captions':['Low-rise buildings around a planted courtyard','The arrival facade','A courtyard sheltered by timber pergolas','A route through the healing garden','An accessible path along the landscaped edge','Stone, timber and the facade rhythm'],'filmNote':'The construction sequence is a visual narrative of the design.'},
 {'id':'ain-tarma','number':'02','section':'Exterior','title':'Ain Tarma Residential Building','type':'Residential · Facade redevelopment','location':'Ain Tarma','heading':'A lighter facade, with a softer edge.','body':'Light cladding is balanced by dark and bronze-toned vertical elements. Curved balconies soften the corners, while glass balustrades keep the facade open. The entrance and material details bring the larger composition down to street level.','captions':['The residential building at street level','Curved balconies and glass balustrades','The entrance at pedestrian level','The meeting of cladding and vertical screens']},
 {'id':'al-hafez','number':'03','section':'Exterior','title':'AL-HAFEZ','type':'Commercial / Industrial','heading':'A clear identity across a larger site.','body':'Light volumes and charcoal frames give the commercial and industrial buildings a shared architectural language. Vertical screens and glazing articulate the main frontage, while the aerial views reveal the relationship between the built edges and the wider site.','captions':['The commercial and industrial frontage','An aerial reading of the site','Charcoal frames around the corner glazing']},
 {'id':'al-tall-villa','number':'04','section':'Exterior','title':'Al-Tall Private Villa','type':'Private residence · Architecture & landscape','location':'Al-Tall','heading':'An arrival shaped by the garden.','body':'Planted paths, a water feature and sheltered seating lead toward the villa. The garden extends the experience of the house through pergolas, evening light and places to pause. The shared film continues inside to the duplex and its curved stair.','captions':['The villa and its garden approach','Water and light along the garden path','The principal entrance','A sheltered outdoor seating area','The pergola and garden at dusk'],'filmNote':'The construction sequence is a visual narrative of the design.'},
 {'id':'damascene-restaurant','number':'05','section':'Exterior','title':'Traditional Damascene Restaurant','type':'Hospitality · Courtyard restaurant','heading':'A courtyard at the heart of the experience.','body':'A fountain anchors the open courtyard, with a stair linking the ground-floor tables to an upper terrace. Stone arches, timber, carved details and climbing plants give the spaces their Damascene character. The same courtyard becomes a quieter setting as day turns to evening.','captions':['Dining around the courtyard fountain','The upper terrace and timber balustrade','The stair connecting the two levels','A view into the courtyard from above','The courtyard after sunset']},
 {'id':'al-tall-duplex','number':'I 01','section':'Interior','title':'Al-Tall Duplex Villa','type':'Residential interior · Duplex','location':'Al-Tall','heading':'A curved stair as the spatial centre.','body':'The sculptural stair connects the two levels and shapes the views between the entrance, dining room and living space. Timber, light surfaces and integrated lighting continue across the interior, with detailed walls giving each area its own character.','captions':['The curved stair and connected living space','The dining room beneath the stair','Living space and media wall','The entrance sequence'],'sharedFilm':'al-tall-villa'},
 {'id':'neoclassical','number':'I 02','section':'Interior','title':'Neoclassical Living & Dining','type':'Residential interior · Neoclassical','heading':'Symmetry, proportion and crafted detail.','body':'The living and dining spaces are organised around a balanced composition of furniture, pilasters and wall panels. The ceiling ornament, chandelier and fireplace create a sequence of focal points, while textiles and warm light soften the carved surfaces.','captions':['The living and dining composition','A symmetrical dining setting','Ceiling ornament and chandelier','Pilasters, curtains and wall panels','Upholstery and carved details']},
 {'id':'paint-showroom','number':'I 03','section':'Interior','title':'Paint Showroom','type':'Retail interior · Paint and material display','heading':'A structural element becomes a display of craft.','body':'Bands of vertical timber slats wrap diagonally around the columns, alternating with exposed light cladding. Concealed light traces the boundaries between the two. Shelves, sample walls and a seating area organise the showroom around a clear material experience.','captions':['The showroom and its timber-wrapped columns','Alternating timber bands and exposed light cladding','Display shelves along the circulation route','The colour sample wall and seating area','The organisation of shelves and display stands']},
 {'id':'open-plan-study','number':'I 04','section':'Interior','title':'Warm Open-Plan Living','type':'Course study · Living / Dining / Kitchen','heading':'One room, connected uses.','body':'A study in arranging living, dining and kitchen functions within a shared open space. Timber, soft upholstery and a restrained material palette connect the zones, while furniture and lighting establish their individual character.','captions':['Living and dining within one open space','The dining area and kitchen beyond','The living area facing the dining and kitchen zones'],'course':True},
 {'id':'bedroom-study','number':'I 05','section':'Interior','title':'Red / Black Bedroom','type':'Course study · Residential interior','heading':'A controlled contrast of colour and light.','body':'A bedroom study combining dark joinery, warm lighting and red accents. The bed wall, glazed wardrobe and ceiling composition are developed as a coordinated interior, exploring the relationship between contrast, texture and proportion.','captions':['The bed wall and contrasting red accents','Material and lighting details at the bed','The bedroom and glazed wardrobe'],'course':True}
]

def image_tag(asset,alt,hero=False,drawing=False):
    srcset='' if drawing else f' srcset="{asset["small"]} {asset["smallWidth"]}w, {asset["src"]} {asset["width"]}w" sizes="(max-width: 700px) calc(100vw - 40px), 90vw"'
    load='fetchpriority="high"' if hero else 'loading="lazy" decoding="async"'
    return f'<img src="{asset["src"]}"{srcset} width="{asset["width"]}" height="{asset["height"]}" alt="{E(alt)}" {load}>'

def figure(asset,caption,hero=False,drawing=False,classes=''):
    picture=image_tag(asset,caption,hero,drawing)
    if not drawing and asset.get('full'):
        picture=f'<a class="render-link" href="{asset["full"]}" data-full-width="{asset["fullWidth"]}" data-full-height="{asset["fullHeight"]}" aria-label="View full size: {E(caption)}" aria-haspopup="dialog">{picture}<span class="render-expand" aria-hidden="true">View full size ↗</span></a>'
    return f'<figure class="{classes}">{picture}<figcaption>{E(caption)}</figcaption></figure>'

def film(project,video):
    identifier=project['id'];poster=assets[identifier]['images'][0]
    ratio=video['width']/video['height'];duration=video['duration']
    film_index=[p['id'] for p in projects if p['id'] in videos].index(identifier)+1
    return f'''<section class="film" id="{identifier}-film" tabindex="0" aria-label="{E(project['title'])} film" data-duration="{duration}" data-ratio="{ratio}" data-pixels-per-second="{video['pixelsPerSecond']}" data-hold="0.035">
      <div class="film-stage"><p class="film-context">{E(project["title"])}</p><div class="film-picture" style="--film-ratio:{ratio}">
        <img class="film-poster" src="{poster['src']}" width="{poster['width']}" height="{poster['height']}" alt="{E(project['captions'][0])}" loading="lazy">
        <video data-src="{video['src']}" poster="{poster['src']}" width="{video['width']}" height="{video['height']}" muted playsinline preload="none" controls aria-label="{E(project['title'])} film"></video><div class="film-identity" aria-hidden="true"><span>{project['section']} / Film {film_index:02} — 05</span><strong>{E(project['title'])}</strong></div></div>
        <div class="film-toolbar"><span class="film-instruction">Scroll to explore the film</span><span class="film-time">00:00</span><button class="film-mode" type="button">Use playback controls</button></div>
        <div class="film-progress" role="progressbar" aria-label="Film position" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><span></span></div>
      </div></section>
      <noscript><style>#{identifier}-film{{display:none}}</style><video class="plain-film" src="{video['src']}" poster="{poster['src']}" controls muted playsinline preload="none" width="{video['width']}" height="{video['height']}"></video></noscript>'''

def project_html(project,index):
    identifier=project['id'];a=assets[identifier];imgs=a['images'];captions=project['captions']
    assert len(captions)==len(imgs)
    place=f'<span class="project-location">{E(project["location"])}</span>' if project.get('location') else ''
    opening=f'''<article class="project" id="{identifier}" data-folder="{a['folder']}"><header class="project-heading"><span class="project-number">{project['number']}</span><div><p class="eyebrow">{E(project['type'])}</p><h3>{E(project['title'])}</h3>{place}</div></header>'''
    if identifier in videos:opening+=film(project,videos[identifier])
    else:opening+=figure(imgs[0],captions[0],hero=index==0,classes='hero-image')
    if project.get('filmPending'):opening+='<p class="film-pending">Film to follow</p>'
    opening+=f'<div class="project-story"><h4>{E(project["heading"])}</h4><div><p>{E(project["body"])}</p>'
    if project.get('filmNote'):opening+=f'<p class="project-note">{E(project["filmNote"])}</p>'
    if project.get('sharedFilm'):opening+='<a class="inline-reference" href="#al-tall-villa-film">Exterior & interior film — in the villa project ↑</a>'
    if project.get('course'):opening+='<p class="course-credit">Course-based exercise<br>Role: course study and visualisation<br>Course source: <span lang="ar" dir="rtl">محمد سويد</span></p>'
    opening+='</div></div>'
    if identifier in videos:opening+=figure(imgs[0],captions[0],classes='gallery-wide')
    rest=list(zip(imgs[1:],captions[1:]))
    for j in range(0,len(rest),2):
        group=rest[j:j+2]
        if len(group)==2:opening+='<div class="image-pair">'+''.join(figure(im,cap) for im,cap in group)+'</div>'
        else:opening+=figure(group[0][0],group[0][1],classes='gallery-wide')
    if a['drawings']:
        drawings=a['drawings'];units=' · Dimensions in centimetres' if identifier in ['al-tall-duplex','neoclassical'] else ''
        opening+=f'<section class="drawings" aria-label="{E(project["title"])} shop drawings"><div class="drawings-heading"><h4>Shop drawings</h4><p>{len(drawings):02} sheets{units}</p></div>'
        remaining=len(drawings);row_remaining=0
        for drawing in drawings:
            if not row_remaining:
                row_remaining=3 if remaining%3==0 else 2
                opening+=f'<div class="drawing-row drawing-row--{row_remaining}">'
            lines=drawing['text'].splitlines();title=lines[2];match=re.search(r'(?m)^[HVIN]-\d{3}$',drawing['text']);code=match.group(0) if match else f'{drawing["page"]:02}'
            caption=f'{code} / {title}'
            opening+=f'<figure class="drawing-sheet"><div class="sheet-paper">{image_tag(drawing,caption,drawing=True)}</div><figcaption><span>{E(caption)}</span><button class="sheet-size" type="button" aria-expanded="false" aria-label="Enlarge {E(caption)}" hidden>Enlarge <span aria-hidden="true">↗</span></button></figcaption></figure>'
            remaining-=1;row_remaining-=1
            if not row_remaining:opening+='</div>'
        opening+='</section>'
    opening+='</article>'
    return opening

head='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#f4f4f0"><title>AMR — Amr Alkhatib | Architecture & Interiors</title><meta name="description" content="Architectural portfolio of Amr Alkhatib: architecture, interiors, project films and shop drawings."><link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="styles.css"><script src="scroll-films.js" defer></script><script src="portrait-editor.js" defer></script><script src="drawing-layout.js" defer></script></head><body>
<a class="skip-link" href="#exterior">Skip to projects</a><header class="site-header"><a class="wordmark" href="#top" aria-label="AMR, back to top">AMR<span>PORTFOLIO</span></a><nav aria-label="Main navigation"><a href="#exterior">Exterior</a><a href="#interior">Interior</a><a href="#about">About</a><a href="#contact">Contact</a></nav></header>
<main id="top"><section class="intro"><p class="eyebrow">Amr Alkhatib · Architecture & interiors</p><div class="intro-title"><h1>AMR</h1><p>Selected<br><em>works.</em></p></div><div class="intro-bottom"><p>A collection of spaces, from the scale of the building to the detail of the interior.</p><a href="#exterior">Explore the projects <span aria-hidden="true">↓</span></a></div></section>'''
parts=[head]
for section in ['Exterior','Interior']:
    section_no='01' if section=='Exterior' else '02'
    section_note='Buildings, courtyards and landscapes.' if section=='Exterior' else 'Rooms, materials and the details of living.'
    parts.append(f'<section id="{section.lower()}" class="collection"><div class="collection-heading"><div><p class="eyebrow">{section_no} / Selected projects</p><h2>{section}</h2></div><p class="collection-note">{section_note}<span>05 projects</span></p></div>')
    parts.extend(project_html(p,projects.index(p)) for p in projects if p['section']==section)
    parts.append('</section>')
parts.append('''<section id="about" class="about"><div class="about-heading"><p class="eyebrow">About</p><h2>Amr<br><em>Alkhatib.</em></h2></div><div class="about-layout"><div class="portrait-column"><img id="amr-portrait" src="media/amr-profile.webp" width="941" height="1672" alt="Portrait of Amr Alkhatib" loading="lazy"><button id="edit-portrait" type="button" hidden aria-controls="portrait-editor" aria-expanded="false">Change portrait</button><form id="portrait-editor" hidden><label for="portrait-file">Choose a new portrait</label><input id="portrait-file" type="file" accept="image/jpeg,image/png,image/webp"><p class="field-hint">JPEG, PNG or WebP · up to 8 MB</p><img class="portrait-preview" alt="Preview of your selected portrait" hidden><div class="editor-actions"><button type="submit" disabled>Save portrait</button><button class="restore-portrait" type="button">Restore default</button></div><p role="status" aria-live="polite"></p></form></div><div class="about-copy"><p class="eyebrow">Architectural engineer</p><p class="about-lead">Residential architecture and interiors, developed through clear spatial concepts, balanced proportions and thoughtful material choices.</p><p>My work explores the relationship between the building, its surroundings and the atmosphere of the interior — from the expression of a facade to the details of everyday spaces.</p><dl><div><dt>Education</dt><dd>Architectural Engineering<br>Faculty of Architecture, University of Damascus</dd></div><div><dt>Focus</dt><dd>Residential & interior design<br>Concept development & visualisation</dd></div><div><dt>Tools</dt><dd>3ds Max · AutoCAD · Revit · Lumion<br>Photoshop · Premiere Pro</dd></div></dl></div></div></section>
<section id="contact" class="contact"><p class="eyebrow">Contact</p><div class="contact-layout"><h2>Let’s talk<br><em>architecture.</em></h2><div class="contact-links"><a href="mailto:amralkhatibamr@gmail.com"><span>Email</span>amralkhatibamr@gmail.com</a><a href="tel:+963992321070"><span>Phone</span>+963 992 321 070</a><a href="tel:+963965543307"><span>Phone</span>+963 965 543 307</a><a href="https://www.instagram.com/arch_amralkhatib/" rel="noopener noreferrer"><span>Instagram</span>@arch_amralkhatib</a></div></div></section></main><footer><span>AMR PORTFOLIO</span><a href="#top">Back to top ↑</a></footer></body></html>''')
document='\n'.join(parts)
about_start=document.index('<section id="about"')
about_end=document.index('<section id="contact"',about_start)
about=document[about_start:about_end]
about=about.replace('class="about"','class="about about-first"',1)
about=about.replace('<div class="about-heading"><p class="eyebrow">About</p><h2>Amr<br><em>Alkhatib.</em></h2></div>','<p class="profile-overline eyebrow">Architecture & interiors / Selected works</p>')
about=about.replace('<div class="about-copy">','<div class="about-copy"><h1 class="profile-name">Amr<br><em>Alkhatib.</em></h1>',1)
about=about.replace('</form></div><div class="about-copy">','</form><div class="profile-practice"><p class="eyebrow">Experience & practice</p><ol><li><span>2022 — 2025</span><strong>Academic architectural projects</strong><p>Architectural studies and design development.</p></li><li><span>Interiors</span><strong>Residential & commercial spaces</strong><p>Spatial quality, atmosphere and functional layouts.</p></li><li><span>Independent work</span><strong>Concept & visualisation</strong><p>Developing and communicating architectural ideas.</p></li></ol></div></div><div class="about-copy">')
about=about.replace('My work explores the relationship between the building, its surroundings and the atmosphere of the interior — from the expression of a facade to the details of everyday spaces.','My work explores the relationship between a building, its surroundings and the atmosphere of the interior. I am particularly interested in contemporary residential architecture, refined facade expression and comfortable interior spaces.</p><p class="profile-detail">I develop ideas through clear layouts, balanced proportions and thoughtful material selection. My work includes academic architectural projects, residential and commercial interiors, and independent concept and visualisation studies.')
about=about.replace('</dl></div></div></section>','</dl><a class="profile-explore" href="#exterior">Explore the projects <span aria-hidden="true">↓</span></a></div></div></section>')
intro_start=document.index('<section class="intro"')
exterior_start=document.index('<section id="exterior"',intro_start)
document=document[:intro_start]+about+document[exterior_start:about_start]+document[about_end:]
document=document.replace('<a href="#exterior">Exterior</a><a href="#interior">Interior</a><a href="#about">About</a>','<a href="#about">About</a><a href="#project-index">Index</a><a href="#exterior">Exterior</a><a href="#interior">Interior</a>')
index_html='<section id="project-index" class="project-index" aria-labelledby="index-title"><div class="index-intro"><div><p class="eyebrow">The portfolio / 10 selected projects</p><h2 id="index-title">A collection<br>of <em>perspectives.</em></h2></div><p class="index-description">From buildings and landscapes to the character of a room.<span>Explore a project, or continue through the collection.</span></p></div><div class="index-columns">'
for section in ['Exterior','Interior']:
    index_html+=f'<nav class="index-column" aria-label="{section} project index"><div class="index-group-heading"><h3>{section}</h3><span>01 — 05</span></div><ol>'
    for project in projects:
        if project['section']!=section:continue
        index_html+=f'<li><a href="#{project["id"]}"><span class="index-number">{project["number"]}</span><span class="index-project"><strong>{E(project["title"])}</strong><small>{E(project["type"])}</small></span><span class="index-arrow" aria-hidden="true">↗</span></a></li>'
    index_html+='</ol></nav>'
index_html+='</div><div class="index-footer"><span>Architecture. Interiors. Detail.</span><a href="#exterior">Begin with Exterior <span aria-hidden="true">↓</span></a></div></section>'
document=document.replace('<section id="exterior"',index_html+'<section id="exterior"',1)
document=document.replace('<a class="profile-explore" href="#exterior">Explore the projects','<a class="profile-explore" href="#project-index">Browse the collection')
document=document.replace('<script src="drawing-layout.js" defer></script>','<script src="drawing-layout.js" defer></script><script src="render-viewer.js" defer></script>')
document=document.replace('</body>','<dialog id="render-viewer" aria-labelledby="render-viewer-title"><header class="render-viewer-header"><p id="render-viewer-title"></p><button class="render-viewer-close" type="button" aria-label="Close full-size image" autofocus>Close <span aria-hidden="true">×</span></button></header><div class="render-viewer-stage"><img class="render-viewer-image" alt="Full-size project render"></div><p class="render-viewer-status" role="status" aria-live="polite"></p></dialog></body>')
# GitHub Pages serves static files. Portrait changes are made through the repository.
document=document.replace('<script src="portrait-editor.js" defer></script>','')
document=re.sub(r'<button id="edit-portrait".*?</form>','',document,flags=re.S)
(public/'index.html').write_text(document,encoding='utf-8')
content=[]
for project in projects:
    item=dict(project);a=assets[item['id']];item['images']=[{**image,'caption':caption} for image,caption in zip(a['images'],item['captions'])];item['drawings']=[{k:v for k,v in im.items() if k!='text'} for im in a['drawings']];item['video']={k:v for k,v in videos[item['id']].items() if k!='sourceSha256'} if item['id'] in videos else None;content.append(item)
(site/'content.json').write_text(json.dumps(content,ensure_ascii=False,indent=2),encoding='utf-8')
print('BUILT 10 PROJECTS / 5 FILMS / 43 RENDERS / 24 DRAWING SHEETS',flush=True)

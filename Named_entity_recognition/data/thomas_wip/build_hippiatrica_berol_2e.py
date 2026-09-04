#!/usr/bin/env python3
"""Reconstruct zoo80/2e.xml (Hippiatrica Berolinensia, English translation)
from hippiatrica_berol_structure.pkl (the source div/p tree, corrected after
the source-XML bug fix described in hippiat_berol_en_batch33.py's header)
and the 48 hippiat_berol_en_batchN.py translation files, substituting
English text for each Greek <p> in document order, preserving the exact
div type/n nesting found in the source.
"""
import pickle
from xml.sax.saxutils import escape

STRUCT = "/home/kossi/Projets/zoomathia/Named_entity_recognition/data/thomas_wip/hippiatrica_berol_structure.pkl"
OUT = "/home/kossi/Projets/zoomathia/Named_entity_recognition/data/zoo/zoo80/2e.xml"

# --- load all 48 batches in order ---
all_paragraphs = []
for i in range(1, 49):
    mod = __import__(f"hippiat_berol_en_batch{i}")
    batch = getattr(mod, f"BATCH{i}")
    all_paragraphs.extend(batch)

with open(STRUCT, "rb") as f:
    structure = pickle.load(f)

print(f"Loaded {len(all_paragraphs)} translated paragraphs.")


def render_nodes(nodes, indent):
    out = []
    pad = "  " * indent
    for node in nodes:
        if node["kind"] == "p":
            text = all_paragraphs[node["idx"]]
            out.append(f'{pad}<p>{escape(text)}</p>')
        elif node["kind"] == "div":
            attrs = f' type="{escape(node["type"])}"' if node.get("type") else ""
            n = node.get("n")
            attrs += f' n="{escape(n)}"' if n is not None else ""
            children = node.get("children", [])
            if children:
                out.append(f'{pad}<div{attrs}>')
                out.append(render_nodes(children, indent + 1))
                out.append(f'{pad}</div>')
            else:
                out.append(f'{pad}<div{attrs}/>')
    return "\n".join(out)


body_content = render_nodes(structure, 0)

HEADER = """<?xml version='1.0' encoding='UTF-8'?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title xml:lang="en">Hippiatrica Berolinensia; or, The Berlin Hippiatrica</title>
        <author>
          <persName>HIPPIATRICA</persName>
        </author>
        <respStmt>
          <persName>Equipe Zoomathia (traduction automatisee)</persName>
          <resp>traducteur (IA, non relue), 2026</resp>
        </respStmt>
      </titleStmt>
      <publicationStmt>
        <publisher>Projet Zoomathia (ANR-21-CE27-0012)</publisher>
        <pubPlace>Universite Cote d'Azur, Nice, France</pubPlace>
        <date when="2026-09-04">2026-09-04</date>
        <availability>
          <licence target="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</licence>
        </availability>
        <idno type="zoomathia"/>
      </publicationStmt>
      <sourceDesc>
        <p>Traduction anglaise auto-generee (IA, non relue par un helleniste) a partir du
        texte grec deja present dans le corpus zoomathia sous zoo80/2g (Hippiatrica
        Berolinensia, compilation byzantine de medecine veterinaire equine transmise sous
        le nom collectif de plusieurs auteurs anciens cites nommement dans le texte meme :
        Apsyrtus, Hierocles, Pelagonius, Theomnestus, Eumelus, Hippocrates, Anatolius,
        entre autres). Le decoupage en 3047 unites de traduction reprend fidelement, dans
        l'ordre du document, la structure de divisions du fichier source (types
        book/chapter/section/subsection et leurs numeros n, lesquels renvoient au systeme
        de numerotation comparative de l'edition critique moderne recoupant plusieurs
        temoins manuscrits et ne correspondent donc pas a une numerotation continue
        simple). Les paragraphes qui ne contenaient que de purs reperes d'apparat
        (numeros isoles, lettres seules du type "t"/"t1") ont ete silencieusement retires
        de l'extraction quand ils constituaient tout le contenu d'un paragraphe source ;
        lorsqu'un tel repere n'etait qu'un prefixe accole a du texte reel dans le meme
        paragraphe, il a ete omis de la traduction sans affecter le texte substantiel.
        Une poignee de reperes isoles qui subsistaient neanmoins comme entrees de
        traduction distinctes ont ete rendus explicitement par la mention entre crochets
        '[apparatus reference marker "..."]'. Les lacunes du manuscrit (signalees dans le
        texte source par des points de suspension ou des passages manifestement
        interrompus) sont rendues par la mention explicite "[lacuna]" plutot que comblees
        par conjecture. Le texte source zoo80/2g.xml contenait une erreur de balisage
        XML corrigee au moment de cette traduction : une balise fermante &lt;/p&gt; manquante
        juste apres la recette "Aristos... pros ta kata neuron traumata" (a la frontiere
        des sections 84/84.1.1) avait pour consequence, en XML generique bien forme mais
        semantiquement incorrect, d'imbriquer tout le reste de l'ouvrage (chapitres 84 a
        130, soit plus de 960 paragraphes reels) a l'interieur de ce seul paragraphe non
        ferme, le rendant invisible a l'extraction automatique standard. Cette erreur a
        ete localisee et corrigee dans le fichier source avant l'extraction finale ayant
        servi de base a la presente traduction, permettant de traduire l'integralite du
        texte disponible plutot que seulement les 2084 premiers paragraphes initialement
        detectes. Ce texte est une compilation pharmacologique et hippiatrique tres dense
        (mesures grecques/byzantines rendues en anglais courant, non converties :
        litra/"pound", ounce/oungia, cotyle/"cotyla", drachme/"drachm", statere/"stater"),
        melangeant recettes veterinaires, notes d'anatomie et de conformation du cheval
        (dentition, catalogue des races regionales), et un vaste formulaire pharmaceutique
        final de plusieurs centaines de recettes composees (emplatres, onguents,
        cataplasmes, collyres) largement partage avec d'autres temoins de la compilation
        hippiatrique. Traduction fournie a titre de meilleur effort ; a verifier par un
        helleniste specialiste de medecine veterinaire antique avant toute citation
        savante. Correspond au texte grec deja present dans le corpus sous zoo80/2g.</p>
      </sourceDesc>
    </fileDesc>
    <profileDesc>
      <langUsage>
        <language ident="en">anglais</language>
      </langUsage>
      <textClass>
        <keywords scheme="zoomathia">
          <term>Zoomathia</term>
          <term>animaux</term>
          <term>tardo-antique (300 - 700 ap. J.-C.)</term>
          <term>anglais</term>
          <term>traduction automatique</term>
        </keywords>
      </textClass>
    </profileDesc>
  </teiHeader>
  <text>
    <body>
"""

FOOTER = """
    </body>
  </text>
</TEI>
"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(HEADER)
    f.write(body_content)
    f.write(FOOTER)

print(f"Wrote {OUT}")

# sanity check: reparse and count paragraphs
from lxml import etree
tree = etree.parse(OUT)
ns = {"tei": "http://www.tei-c.org/ns/1.0"}
ps = tree.findall(".//tei:p", ns)
print(f"Reparsed OK: {len(ps)} <p> elements found (expected {len(all_paragraphs)})")

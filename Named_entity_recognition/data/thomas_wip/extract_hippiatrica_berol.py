#!/usr/bin/env python3
"""Extract Hippiatrica Berolinensia (zoo80/2g.xml) into a plain-text reference
file with global paragraph indices, for sequential translation, and pickle the
source tree structure (as a list of top-level <div> elements, each holding its
nested div/p structure) so a build script can later reconstruct zoo80/2e.xml
with the same div type/n nesting, substituting English text for each <p>.

Like its already-translated sibling zoo80/1e (Hippiatrica Cantabrigiensia),
this file's div book/chapter/section numbering follows the modern critical
edition's comparative apparatus (cross-referencing several manuscript
witnesses - Cantabrigiensis, Berolinensis, Parisina) rather than a simple
continuous numbering, so numbers jump around; the div structure is preserved
exactly as found, in document order, with English paragraphs substituted in
place of Greek ones. A handful of paragraphs contain nothing but pure
apparatus/reference markers (bare numbers) and are skipped, not translated.
"""
import pickle
import re
from lxml import etree

SRC = "/home/kossi/Projets/zoomathia/Named_entity_recognition/data/zoo/zoo80/2g.xml"
NS = {"tei": "http://www.tei-c.org/ns/1.0"}

tree = etree.parse(SRC)
root = tree.getroot()
body = root.find(".//tei:body", NS)


def local(tag):
    return etree.QName(tag).localname


def is_apparatus(text):
    t = text.strip()
    if len(t) < 3:
        return True
    if re.match(r"^[\d.\s]+$", t):
        return True
    return False


# Structure: list of nodes; each node is either
#   {"kind": "div", "type": ..., "n": ..., "children": [nodes...]}
#   {"kind": "p", "idx": N}   (idx assigned only to real, non-apparatus paragraphs)
# Apparatus-only / empty <p> are dropped entirely (not even placeholders).
paragraphs = []  # list of greek text, in order, index = position (0-based)


def walk(elem):
    nodes = []
    for child in elem:
        tag = local(child.tag)
        if tag == "div":
            sub = walk(child)
            nodes.append({
                "kind": "div",
                "type": child.get("type"),
                "n": child.get("n"),
                "children": sub,
            })
        elif tag == "p":
            text = "".join(child.itertext())
            text = re.sub(r"\s+", " ", text).strip()
            if text and not is_apparatus(text):
                paragraphs.append(text)
                nodes.append({"kind": "p", "idx": len(paragraphs) - 1})
            # else: dropped silently (apparatus marker or empty)
        # milestone and other elements: ignored (structural markers only)
    return nodes


structure = walk(body)

print(f"Total real paragraphs: {len(paragraphs)}")

with open("/home/kossi/Projets/zoomathia/Named_entity_recognition/data/thomas_wip/hippiatrica_berol_structure.pkl", "wb") as f:
    pickle.dump(structure, f)

with open("/home/kossi/Projets/zoomathia/Named_entity_recognition/data/thomas_wip/hippiatrica_berol_reference.txt", "w", encoding="utf-8") as f:
    for i, p in enumerate(paragraphs, 1):
        f.write(f"[{i}]\nGRC: {p}\n\n")

print("Wrote hippiatrica_berol_structure.pkl and hippiatrica_berol_reference.txt")

import os
import shutil
import subprocess
from pymongo import MongoClient
import logging

MONGO_URL = "mongodb://127.0.0.1:27017"
DB_NAME = "Ner"
METADATA_COLLECTION = "Metadata"

OUTPUT_DIR = "output"
TEMP_DIR = "temp"

MORPH_PROPERTIES = "morph.properties"
ANNOTATION_MAPPING = "annotation.ttl"
PARAGRAPH_MAPPING = "paragraph.ttl"
LINK_MAPPING = "link.ttl"
METADATA_MAPPING = "metadata.ttl"
VOCAB_MAPPING = "vocab.ttl"

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)


def escape_mongo_regex(uri):
    """Échappe les caractères spéciaux pour les requêtes $regex MongoDB"""
    return uri.replace(".", "\\\\.").replace("(", "\\\\(").replace(")", "\\\\)")


def get_texts():
    logging.info("Connecting to MongoDB...")
    client = MongoClient(MONGO_URL)
    collection = client[DB_NAME][METADATA_COLLECTION]
    texts = {}

    for doc in collection.find({}, {"uri": 1, "_id": 1, "title": 1, "prov": 1}):
        if "uri" not in doc:
            continue
        raw_id = doc.get("_id")
        if not raw_id:
            continue

        prov_raw = doc.get("prov")
        if not prov_raw:
            logging.warning(f"Texte ignoré (aucun attribut 'prov' trouvé) pour l'id: {raw_id}")
            continue

        prov_filename = os.path.basename(prov_raw.replace("\\", "/"))
        prov_clean = os.path.splitext(prov_filename)[0]

        if raw_id not in texts:
            texts[raw_id] = {
                "id": raw_id,
                "uri": doc["uri"],
                "title": doc.get("title", raw_id),
                "prov": prov_clean
            }

    client.close()
    logging.info(f"{len(texts)} unique texts found in Metadata.")
    return list(texts.values())


def create_filtered_paragraph(text_uri, output_mapping):
    with open(PARAGRAPH_MAPPING, "r", encoding="utf-8") as f:
        content = f.read()

    if "/la" in text_uri:
        content = content.replace('rr:datatype xsd:string;', 'rr:language "la"')
        content = content.replace('rr:language "grc"', 'rr:language "la"')
        content = content.replace('rr:language "en"', 'rr:language "la"')
    elif "/grc" in text_uri:
        content = content.replace('rr:datatype xsd:string;', 'rr:language "grc"')
        content = content.replace('rr:language "la"', 'rr:language "grc"')
        content = content.replace('rr:language "en"', 'rr:language "grc"')
    elif "/en" in text_uri:
        content = content.replace('rr:datatype xsd:string;', 'rr:language "en"')
        content = content.replace('rr:language "la"', 'rr:language "en"')
        content = content.replace('rr:language "grc"', 'rr:language "en"')

    query = f"db.Paragraph.find({{ 'parent_uri': {{ '$regex': '{escape_mongo_regex(text_uri)}' }} }})"

    if "db.Paragraph.find()" not in content:
        logging.warning("db.Paragraph.find() not found in paragraph.ttl")
    else:
        content = content.replace("db.Paragraph.find()", query)

    with open(output_mapping, "w", encoding="utf-8") as f:
        f.write(content)


def create_filtered_metadata(text_uri, output_mapping):
    with open(METADATA_MAPPING, "r", encoding="utf-8") as f:
        content = f.read()
    query = f"db.Metadata.find({{ 'uri': '{text_uri}' }})"
    content = content.replace("db.Metadata.find()", query)
    with open(output_mapping, "w", encoding="utf-8") as f:
        f.write(content)


def create_filtered_link(text_uri, output_mapping):
    with open(LINK_MAPPING, "r", encoding="utf-8") as f:
        content = f.read()
    query1 = f'db.Link.find({{"type": {{$ne: "Work"}}, "parent_uri": {{$regex: "{escape_mongo_regex(text_uri)}"}}}})'
    query2 = f'db.Link.find({{"type": "Work", "parent_uri": "{text_uri}"}})'
    content = content.replace('db.Link.find({"type": {$ne: "Work"}})', query1)
    content = content.replace('db.Link.find({"type" : "Work"})', query2)
    with open(output_mapping, "w", encoding="utf-8") as f:
        f.write(content)


def create_filtered_vocab(text_uri, output_mapping):
    with open(VOCAB_MAPPING, "r", encoding="utf-8") as f:
        content = f.read()
    query = f"db.Annotation.find({{ 'origin': {{$ne: 'zoomathia'}}, 'paragraph_uri': {{ '$regex': '{escape_mongo_regex(text_uri)}' }} }})"
    content = content.replace("db.Annotation.find({'origin' : {$ne : 'zoomathia'}})", query)
    with open(output_mapping, "w", encoding="utf-8") as f:
        f.write(content)


def create_filtered_annotation(text_uri, output_mapping):
    with open(ANNOTATION_MAPPING, "r", encoding="utf-8") as f:
        content = f.read()
    query = f"db.Annotation.find({{ 'paragraph_uri': {{ '$regex': '{escape_mongo_regex(text_uri)}' }} }})"
    if "db.Annotation.find()" not in content:
        logging.warning("db.Annotation.find() not found in annotation.ttl")
    else:
        content = content.replace("db.Annotation.find()", query)
    with open(output_mapping, "w", encoding="utf-8") as f:
        f.write(content)


def generate_paragraph(text):
    if not os.path.exists(PARAGRAPH_MAPPING):
        logging.warning("paragraph.ttl not found.")
        return None
    prov_id = text["prov"]
    temp_map = os.path.join(TEMP_DIR, f"paragraph_{prov_id}_map.ttl")
    out_file = os.path.join(TEMP_DIR, f"paragraph_{prov_id}.ttl")
    create_filtered_paragraph(text["uri"], temp_map)
    run_xr2rml(temp_map, out_file)
    if os.path.exists(temp_map): os.remove(temp_map)
    return out_file if os.path.exists(out_file) else None


def generate_metadata(text):
    prov_id = text["prov"]
    temp_map = os.path.join(TEMP_DIR, f"metadata_{prov_id}_map.ttl")
    out_file = os.path.join(TEMP_DIR, f"metadata_{prov_id}.ttl")
    create_filtered_metadata(text["uri"], temp_map)
    run_xr2rml(temp_map, out_file)
    if os.path.exists(temp_map): os.remove(temp_map)
    return out_file if os.path.exists(out_file) else None


def generate_link(text):
    prov_id = text["prov"]
    temp_map = os.path.join(TEMP_DIR, f"link_{prov_id}_map.ttl")
    out_file = os.path.join(TEMP_DIR, f"link_{prov_id}.ttl")
    create_filtered_link(text["uri"], temp_map)
    run_xr2rml(temp_map, out_file)
    if os.path.exists(temp_map): os.remove(temp_map)
    return out_file if os.path.exists(out_file) else None


def generate_vocab(text):
    prov_id = text["prov"]
    temp_map = os.path.join(TEMP_DIR, f"vocab_{prov_id}_map.ttl")
    out_file = os.path.join(TEMP_DIR, f"vocab_{prov_id}.ttl")
    create_filtered_vocab(text["uri"], temp_map)
    run_xr2rml(temp_map, out_file)
    if os.path.exists(temp_map): os.remove(temp_map)
    return out_file if os.path.exists(out_file) else None


def generate_annotation(text):
    if not os.path.exists(ANNOTATION_MAPPING):
        logging.warning("annotation.ttl not found.")
        return None
    prov_id = text["prov"]
    temp_map = os.path.join(TEMP_DIR, f"annotation_{prov_id}_map.ttl")
    out_file = os.path.join(TEMP_DIR, f"annotation_{prov_id}.ttl")
    create_filtered_annotation(text["uri"], temp_map)
    run_xr2rml(temp_map, out_file)
    if os.path.exists(temp_map): os.remove(temp_map)
    return out_file if os.path.exists(out_file) else None


def create_properties(mapping_file, output_file):
    mapping_file = mapping_file.replace("\\", "/")
    output_file = output_file.replace("\\", "/")
    with open(MORPH_PROPERTIES, "r", encoding="utf-8") as f:
        lines = f.readlines()
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("mappingdocument.file.path="):
            new_lines.append(f"mappingdocument.file.path={mapping_file}\n")
        elif stripped.startswith("output.file.path="):
            new_lines.append(f"output.file.path={output_file}\n")
        else:
            new_lines.append(line)
    temp_properties = os.path.join(TEMP_DIR, "temp.properties")
    with open(temp_properties, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    return temp_properties


def run_xr2rml(mapping_file, output_file):
    properties = create_properties(mapping_file, output_file)
    cmd = [
        "java", "-Xmx4g", "-jar",
        "../morph-xr2rml-dist-1.3.1-jar-with-dependencies.jar",
        "--configDir", ".", "--configFile", properties
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        if not os.path.exists(output_file):
            logging.warning("Java returned success but output file does not exist.")
    else:
        logging.error(f"xR2RML failed. Return code: {result.returncode}")
        if result.stderr.strip(): print(result.stderr)
        if result.stdout.strip(): print(result.stdout)
    if os.path.exists(properties):
        os.remove(properties)


def merge_ttl_files(filepaths, output_path):
    prefixes = set()

    # Extraction des préfixes
    for filepath in filepaths:
        with open(filepath, "r", encoding="utf-8") as infile:
            for line in infile:
                if line.startswith("@prefix"):
                    prefixes.add(line)

    # Écriture du fichier fusionné
    with open(output_path, "w", encoding="utf-8") as outfile:
        for prefix in sorted(prefixes):
            outfile.write(prefix)
        outfile.write("\n")

        for filepath in filepaths:
            with open(filepath, "r", encoding="utf-8") as infile:
                for line in infile:
                    if not line.startswith("@prefix"):
                        outfile.write(line)
            outfile.write("\n")


def process_text(text):
    raw_id = text["id"]
    prov_id = text["prov"]
    title = text["title"]

    logging.info("--------------------------------")
    logging.info(f"Processing Text : {title}")
    logging.info(f"ID (DB) : {raw_id} | Prov : {prov_id}")

    # Création du dossier spécifique pour ce texte avec l'attribut prov
    text_out_dir = os.path.join(OUTPUT_DIR, prov_id)
    os.makedirs(text_out_dir, exist_ok=True)

    files_to_merge = []

    f_meta = generate_metadata(text)
    if f_meta: files_to_merge.append(f_meta)

    f_para = generate_paragraph(text)
    if f_para: files_to_merge.append(f_para)

    f_annot = generate_annotation(text)
    if f_annot: files_to_merge.append(f_annot)

    f_link = generate_link(text)
    if f_link: files_to_merge.append(f_link)

    f_vocab = generate_vocab(text)
    if f_vocab: files_to_merge.append(f_vocab)

    if not files_to_merge:
        logging.warning(f"No graphs generated for {raw_id}")
        return

    # Fusionne les graphes du texte dans le fichier local nommé d'après prov
    text_combined_ttl = os.path.join(text_out_dir, f"{prov_id}.ttl")
    logging.info(f"Merging {len(files_to_merge)} partial graphs into {text_combined_ttl}")
    merge_ttl_files(files_to_merge, text_combined_ttl)

    # Nettoyage des fichiers temporaires spécifiques au texte
    for f in files_to_merge:
        os.remove(f)


def merge_all_graphs(texts):
    logging.info("===================================")
    logging.info("Merging all text graphs into all.ttl...")
    logging.info("===================================")

    output_path = os.path.join(OUTPUT_DIR, "all.ttl")
    files_to_merge = []

    for text in texts:
        prov_id = text["prov"]
        filepath = os.path.join(OUTPUT_DIR, prov_id, f"{prov_id}.ttl")
        if os.path.exists(filepath):
            files_to_merge.append(filepath)

    if not files_to_merge:
        logging.warning("No text graph files found to merge.")
        return

    merge_ttl_files(files_to_merge, output_path)
    logging.info(f"--> all.ttl created ({len(files_to_merge)} files merged)")


# ============================================================
# MAIN
# ============================================================

def main():
    logging.info("===================================")
    logging.info("XR2RML Graph Generation & Merge")
    logging.info("===================================")

    texts = get_texts()

    for text in texts:
        process_text(text)

    merge_all_graphs(texts)

    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

    logging.info("===================================")
    logging.info("Finished.")
    logging.info(f"Global generated files are in {OUTPUT_DIR}/")
    logging.info("===================================")


if __name__ == "__main__":
    main()
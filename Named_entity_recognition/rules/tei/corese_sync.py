#!/usr/bin/env python3
"""Synchronisation d'une oeuvre vers Corese sans redemarrage complet du
conteneur - point 5 de la feuille de route "amelioration du pipeline"
(remplace le cycle manuel couper Corese/remplacer mini.ttl/rallumer,
~4 min et indisponibilite totale du site, par une mise a jour cibleee
de quelques secondes, site disponible en continu).

ARCHITECTURE - pourquoi un "graphe nomme" par oeuvre :

Le graphe de production range aujourd'hui tout dans un seul graphe par
defaut (~40M triplets). Supprimer proprement l'ancienne version d'UNE
oeuvre avant d'inserer la nouvelle demande donc de savoir QUELS triplets
lui appartiennent - or les annotations automatiques (zoo:
AutomaticAnnotation) vivent sous une URI hachee, hors namespace de
l'oeuvre, reliees au texte seulement via des noeuds anonymes
(oa:hasTarget/oa:hasSelector). Un simple FILTER(STRSTARTS(...)) doit
alors tester CHAQUE triplet du graphe : mesure empiriquement a plus de
2 minutes, et instable (a sature le CPU), meme pour une oeuvre de 7
paragraphes.

Solution retenue : donner a chaque oeuvre son propre "graphe nomme"
Corese (GRAPH <uri-de-l-oeuvre> { ... }), confirme experimentalement
transparent pour toutes les requetes de l'application (Corese traite le
graphe par defaut comme l'union de tous les graphes nommes - une
requete SANS clause GRAPH voit aussi bien les anciens texte non migres
que les nouveaux). Des lors, mettre a jour une oeuvre DEJA migree se
resume a "CLEAR GRAPH <uri>" (mesure : 0,1 a quelques secondes, PAS
proportionnel a la taille totale du magasin) suivi d'un INSERT DATA
cible - un cout proportionnel au SEUL contenu de l'oeuvre, jamais aux
~40M triplets du reste du corpus.

MIGRATION (une oeuvre a la fois, pas automatique) : la toute premiere
fois qu'une oeuvre passe par ce mecanisme, son ancienne copie vit
encore dans le graphe par defaut (les 233 oeuvres du corpus y sont
actuellement). Plutot que de risquer un DELETE live couteux/instable
sur le graphe par defaut, la migration modifie mini.ttl SUR DISQUE
(retrait des blocs texte de l'oeuvre + reajout enveloppe dans un bloc
GRAPH <uri> { ... }, meme mecanisme fiable que la fusion chirurgicale
historique - merge_mini_14.py/merge_mini_32.py) puis demande UN
redemarrage de Corese pour charger ce fichier corrige. Cout : le meme
redemarrage complet qu'avant (~4 min), mais plus JAMAIS necessaire
ENSUITE pour cette oeuvre - chaque mise a jour future devient la voie
rapide (CLEAR GRAPH + INSERT, en direct, sans redemarrage).

Utilisable en module (importe par graph-generation.py) ou en CLI :
    python3 corese_sync.py migrate <prov1> [<prov2> ...]   # une fois, puis redemarrer Corese
    python3 corese_sync.py sync    <prov1> [<prov2> ...]   # voie rapide, en direct
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request

MINI_TTL = "/home/kossi/corese_data/mini.ttl"
CORESE_ENDPOINT = "http://localhost:8081/sparql"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


# ---------------------------------------------------------------------------
# Utilitaires communs
# ---------------------------------------------------------------------------

def extract_work_uri(ttl_path):
    """Repere l'URI du noeud `a zoo:Oeuvre` dans un .ttl d'oeuvre."""
    text = open(ttl_path, encoding="utf-8").read()
    m = re.search(r"<([^>]+)>\s*\n\s*a\s+zoo:Oeuvre", text)
    return m.group(1) if m else None


def split_prefixes(ttl_text):
    """Separe les lignes @prefix (converties en forme PREFIX pour SPARQL
    Update) du corps du fichier."""
    prefixes, body = [], []
    for line in ttl_text.splitlines(keepends=True):
        if line.lstrip().startswith("@prefix"):
            m = re.match(r"@prefix\s+(\S+)\s+<([^>]+)>\s*\.", line.strip())
            if m:
                prefixes.append(f"PREFIX {m.group(1)} <{m.group(2)}>")
        else:
            body.append(line)
    return prefixes, "".join(body)


def sparql_update(update_str, endpoint=CORESE_ENDPOINT, timeout=120):
    req = urllib.request.Request(
        endpoint, data=update_str.encode("utf-8"), method="POST",
        headers={"Content-Type": "application/sparql-update"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status


def sparql_query(query, endpoint=CORESE_ENDPOINT, timeout=60):
    req = urllib.request.Request(
        f"{endpoint}?query={urllib.parse.quote(query)}",
        headers={"Accept": "application/sparql-results+json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def sparql_count(endpoint=CORESE_ENDPOINT):
    data = sparql_query("SELECT (COUNT(*) as ?c) WHERE {?s ?p ?o}", endpoint)
    return int(data["results"]["bindings"][0]["c"]["value"])


def is_migrated(work_uri, endpoint=CORESE_ENDPOINT):
    """Vrai si l'oeuvre vit deja dans son propre graphe nomme."""
    data = sparql_query(f"ASK {{ GRAPH <{work_uri}> {{ ?s ?p ?o }} }}", endpoint)
    return bool(data.get("boolean"))


# ---------------------------------------------------------------------------
# Voie rapide (oeuvre deja migree) : CLEAR GRAPH + INSERT, en direct
# ---------------------------------------------------------------------------

CORESE_DATA_DIR = "/home/kossi/corese_data"


def sync_named_graph_live(work_uri, ttl_path, endpoint=CORESE_ENDPOINT):
    """Vide puis recharge le graphe nomme de l'oeuvre, en direct sur
    l'endpoint Corese. Rapide (proportionnel au SEUL contenu de
    l'oeuvre, jamais au reste du magasin) : CLEAR GRAPH est immediat
    (index par graphe), et le rechargement passe par SPARQL Update LOAD
    <file://...> plutot que par INSERT DATA - mesure empiriquement
    ~280 fois plus rapide (0,2 s contre 57,6 s sur un test reel de 7
    paragraphes/~3900 triplets) car LOAD utilise le meme chargeur en
    masse que le demarrage du serveur, alors qu'INSERT DATA traite les
    triplets un par un via le parseur de requetes. Necessite que Corese
    tourne avec l'option -su (superuser) : sans elle, LOAD depuis un
    fichier local est refuse (SafetyException)."""
    tmp_name = f"_sync_{os.path.basename(os.path.dirname(ttl_path))}.ttl"
    tmp_path = os.path.join(CORESE_DATA_DIR, tmp_name)
    try:
        with open(ttl_path, encoding="utf-8") as src, open(tmp_path, "w", encoding="utf-8") as dst:
            dst.write(src.read())

        sparql_update(f"CLEAR GRAPH <{work_uri}>", endpoint)
        sparql_update(
            f"LOAD <file:///usr/local/corese/data/{tmp_name}> INTO GRAPH <{work_uri}>",
            endpoint,
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def sync_named_graph_in_mini_file(work_uri, ttl_path, mini_path=MINI_TTL):
    """Meme mise a jour, appliquee au fichier mini.ttl sur disque : le
    bloc `# ==== GRAPH <uri> ==== GRAPH <uri> { ... }` precedent (s'il
    existe) est retire puis reecrit avec le contenu frais, pour que la
    persistance survive a un futur redemarrage.

    Lecture EN FLUX, ligne par ligne (jamais fin.read() sur le fichier
    entier) : mini.ttl pese ~2,85 Go, et le charger entierement en
    memoire comme chaine Python a fait grimper un premier essai a plus
    de 3 Go de RAM et provoque un OOM-kill du process sur cette
    machine (14 Go de RAM, deja chargee par ailleurs)."""
    marker_start = f"# ==== GRAPH {work_uri} ====\n"
    tmp_path = mini_path + ".tmp_sync"

    with open(mini_path, encoding="utf-8") as fin, open(tmp_path, "w", encoding="utf-8") as fout:
        in_skipped_block = False
        for line in fin:
            if line == marker_start:
                in_skipped_block = True
                continue
            if in_skipped_block and line.startswith("# ==== GRAPH "):
                in_skipped_block = False
            if not in_skipped_block:
                fout.write(line)

        prefixes, body = split_prefixes(open(ttl_path, encoding="utf-8").read())
        fout.write(f"\n{marker_start}")
        fout.write(f"GRAPH <{work_uri}> {{\n{body}\n}}\n")

    os.replace(tmp_path, mini_path)


# ---------------------------------------------------------------------------
# Migration (une fois par oeuvre) : mini.ttl sur disque uniquement,
# necessite un redemarrage de Corese pour prendre effet.
# ---------------------------------------------------------------------------

def migrate_work_in_mini_file(work_uri, ttl_path, mini_path=MINI_TTL):
    """Retire les blocs texte de l'oeuvre du graphe par defaut (un bloc
    appartient a l'oeuvre si l'URI y apparait, comme sujet ou
    reference) et les reecrit dans un bloc GRAPH <uri> { ... } a la fin
    du fichier. Necessite un redemarrage du conteneur Corese pour
    prendre effet - ne touche pas le graphe en direct.

    Detection des blocs : une NOUVELLE entite commence a une ligne non
    indentee debutant par "<" (ou une ligne vide, la ou il y en a) -
    PAS uniquement sur les lignes vides. Verifie empiriquement : la
    majorite de mini.ttl (les parties les plus anciennes) n'a AUCUNE
    ligne vide entre les blocs ; un decoupage par ligne vide seul
    accumule alors un unique bloc geant sans jamais le vider, avec un
    cout memoire proportionnel (mesure : >3,9 Go de RAM avant d'etre
    tue, sur un scan complet du fichier)."""
    markers = (f"<{work_uri}>", f"<{work_uri}/")
    tmp_path = mini_path + ".tmp_migrate"
    kept = dropped = 0

    with open(mini_path, encoding="utf-8") as fin, open(tmp_path, "w", encoding="utf-8") as fout:
        block = []

        def flush():
            nonlocal kept, dropped
            if not block:
                return
            text = "".join(block)
            if text.lstrip().startswith("@prefix") or not any(m in text for m in markers):
                fout.write(text)
                kept += 1
            else:
                dropped += 1

        for line in fin:
            stripped = line.rstrip("\n")
            is_new_entity_start = line.startswith("<")
            is_blank = (stripped == "")
            if (is_new_entity_start or is_blank) and block:
                flush()
                block = []
            if not is_blank:
                block.append(line)
        flush()

        prefixes, body = split_prefixes(open(ttl_path, encoding="utf-8").read())
        fout.write(f"\n# ==== GRAPH {work_uri} ====\n")
        fout.write(f"GRAPH <{work_uri}> {{\n{body}\n}}\n")

    os.replace(tmp_path, mini_path)
    return kept, dropped


def remove_works_from_mini_file(work_uris, mini_path=MINI_TTL):
    """Retire completement (sans reecriture ailleurs) les blocs texte
    de plusieurs oeuvres du graphe par defaut. Meme detection de blocs
    que migrate_work_in_mini_file. Usage : purge definitive (ex.
    contenu sous droits ne devant plus exister dans le graphe), pas une
    migration - rien n'est reajoute. Necessite un redemarrage de Corese
    pour prendre effet."""
    markers = []
    for uri in work_uris:
        markers.append(f"<{uri}>")
        markers.append(f"<{uri}/")
    tmp_path = mini_path + ".tmp_remove"
    kept = dropped = 0

    with open(mini_path, encoding="utf-8") as fin, open(tmp_path, "w", encoding="utf-8") as fout:
        block = []

        def flush():
            nonlocal kept, dropped
            if not block:
                return
            text = "".join(block)
            if text.lstrip().startswith("@prefix") or not any(m in text for m in markers):
                fout.write(text)
                kept += 1
            else:
                dropped += 1

        for line in fin:
            stripped = line.rstrip("\n")
            is_new_entity_start = line.startswith("<")
            is_blank = (stripped == "")
            if (is_new_entity_start or is_blank) and block:
                flush()
                block = []
            if not is_blank:
                block.append(line)
        flush()

    os.replace(tmp_path, mini_path)
    return kept, dropped


# ---------------------------------------------------------------------------
# Points d'entree
# ---------------------------------------------------------------------------

def sync_prov(prov_id, endpoint=CORESE_ENDPOINT, mini_path=MINI_TTL, update_mini_file=True):
    """Voie rapide : suppose l'oeuvre deja migree vers son graphe nomme.
    A utiliser en routine (appelable automatiquement apres chaque
    regeneration de .ttl)."""
    ttl_path = os.path.join(OUTPUT_DIR, prov_id, f"{prov_id}.ttl")
    if not os.path.exists(ttl_path):
        return {"prov": prov_id, "ok": False, "error": f".ttl introuvable : {ttl_path}"}

    work_uri = extract_work_uri(ttl_path)
    if not work_uri:
        return {"prov": prov_id, "ok": False, "error": "URI d'oeuvre introuvable dans le .ttl"}

    result = {"prov": prov_id, "uri": work_uri, "ok": True}
    try:
        if not is_migrated(work_uri, endpoint):
            result["ok"] = False
            result["error"] = (
                "Oeuvre pas encore migree vers un graphe nomme - lancer "
                f"d'abord: python3 corese_sync.py migrate {prov_id}, puis "
                "redemarrer Corese."
            )
            return result
        sync_named_graph_live(work_uri, ttl_path, endpoint)
        # Compte scope au SEUL graphe de l'oeuvre, pas au magasin entier
        # (~40M triplets) : un compte global est un diagnostic couteux et
        # non necessaire a la reussite de la synchro elle-meme - sous
        # charge machine, il peut a lui seul depasser le delai d'attente
        # et faire croire a un echec alors que la synchro a reussi.
        data = sparql_query(
            f"SELECT (COUNT(*) as ?c) WHERE {{ GRAPH <{work_uri}> {{?s ?p ?o}} }}",
            endpoint,
        )
        result["triplets_graphe_oeuvre"] = int(data["results"]["bindings"][0]["c"]["value"])
    except Exception as e:
        result["ok"] = False
        result["error"] = f"Corese injoignable/erreur SPARQL Update : {e}"
        return result

    if update_mini_file:
        try:
            sync_named_graph_in_mini_file(work_uri, ttl_path, mini_path)
        except Exception as e:
            result["mini_ttl_error"] = str(e)

    return result


def migrate_prov(prov_id, mini_path=MINI_TTL):
    """Migration : a lancer une fois par oeuvre, puis redemarrer Corese
    pour que ca prenne effet. N'importe combien d'oeuvres peuvent etre
    migrees avant un seul redemarrage groupe."""
    ttl_path = os.path.join(OUTPUT_DIR, prov_id, f"{prov_id}.ttl")
    if not os.path.exists(ttl_path):
        return {"prov": prov_id, "ok": False, "error": f".ttl introuvable : {ttl_path}"}

    work_uri = extract_work_uri(ttl_path)
    if not work_uri:
        return {"prov": prov_id, "ok": False, "error": "URI d'oeuvre introuvable dans le .ttl"}

    kept, dropped = migrate_work_in_mini_file(work_uri, ttl_path, mini_path)
    return {
        "prov": prov_id, "uri": work_uri, "ok": True,
        "mini_ttl_blocs_gardes": kept, "mini_ttl_blocs_retires": dropped,
        "note": "redemarrer Corese pour que la migration prenne effet",
    }


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("migrate", "sync"):
        print("Usage: python3 corese_sync.py migrate|sync <prov1> [<prov2> ...]")
        sys.exit(1)
    action = migrate_prov if sys.argv[1] == "migrate" else sync_prov
    for prov in sys.argv[2:]:
        print(action(prov))

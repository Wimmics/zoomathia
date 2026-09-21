import os
import pandas as pd

auteurs = pd.read_csv("auteurs_rows.csv")
oeuvres = pd.read_csv("oeuvres_rows.csv")
fichiers = pd.read_csv("fichiers_rows.csv")

LANGUE_CODE = {"grec": "g", "latin": "l", "anglais": "e", "francais": "f", "italien": "i"}

# Numeroter les oeuvres 1,2,3... par auteur (dans l'ordre de leur id)
oeuvres = oeuvres.sort_values(["auteur_id", "id"]).reset_index(drop=True)
oeuvres["numero_oeuvre"] = oeuvres.groupby("auteur_id").cumcount() + 1

# Fusionner fichiers -> oeuvres -> auteurs
df = fichiers.merge(oeuvres, left_on="oeuvre_id", right_on="id", suffixes=("_fichier", "_oeuvre"))
df = df.merge(auteurs, left_on="auteur_id", right_on="id", suffixes=("", "_auteur"))

df["lettre_langue"] = df["langue"].map(LANGUE_CODE).fillna("?")

# Desambiguation : plusieurs fichiers peuvent partager la meme oeuvre et la
# meme langue (ex. Nemesianus a 5 fichiers latins distincts pour sa 1re
# oeuvre) - sans ca ils recevraient tous exactement le meme code_zoo. On
# reprend la meme convention que ajouter_fichier.py utilise deja pour nommer
# les fichiers sur le disque : le premier (par id croissant, ordre d'ajout)
# ne porte pas de suffixe, les suivants recoivent _2, _3...
df = df.sort_values(["auteur_id", "numero_oeuvre", "lettre_langue", "id_fichier"]).reset_index(drop=True)
rang = df.groupby(["auteur_id", "numero_oeuvre", "lettre_langue"]).cumcount() + 1
suffixe = rang.apply(lambda n: "" if n == 1 else f"_{n}")
df["code_zoo"] = "zoo" + df["auteur_id"].astype(str) + "/" + df["numero_oeuvre"].astype(str) + df["lettre_langue"] + suffixe

resultat = df[["nom_fichier", "code_zoo", "nom_canonique", "titre_original", "langue", "statut", "identifiant"]]
resultat = resultat.rename(columns={"identifiant": "ancien_code"})
resultat = resultat.sort_values("code_zoo")

# La colonne "etat" ne vient pas de Supabase (qui ne sait rien de la qualite
# de l'alignement original/traduction) : elle est fusionnee depuis
# alignement_zoo.csv, un fichier tenu a part et suivi par git, justement
# pour survivre a chaque regeneration de ce script. Un code_zoo absent de
# alignement_zoo.csv (fichier jamais audite, ou pas encore ajoute) obtient
# une case vide plutot qu'une erreur.
try:
    alignement = pd.read_csv("alignement_zoo.csv")
    resultat = resultat.merge(alignement, on="code_zoo", how="left")
except FileNotFoundError:
    resultat["etat"] = ""

resultat = resultat[["nom_fichier", "code_zoo", "nom_canonique", "titre_original", "etat", "statut", "langue", "ancien_code"]]

# Corpus actif / archive : determine par la presence reelle du fichier sur
# disque (data/zoo/ ou data/zoo_archive/), pas par une colonne a maintenir a
# la main. Les codes restent calcules sur l'ensemble des fichiers (ci-dessus),
# donc filtrer ici ne change aucun code_zoo.
DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def emplacement(code_zoo):
    dossier, fichier = code_zoo.split("/", 1)
    if os.path.exists(os.path.join(DATA_DIR, "zoo", dossier, fichier + ".xml")):
        return "actif"
    if os.path.exists(os.path.join(DATA_DIR, "zoo_archive", dossier, fichier + ".xml")):
        return "archive"
    return "absent"

resultat["corpus"] = resultat["code_zoo"].apply(emplacement)

# repertoire_codes_zoo.csv : uniquement le corpus actif (celui que traite la
# pipeline). repertoire_codes_archive.csv : les fichiers archives ou absents du
# disque, gardes pour conserver leur code et leur statut de droits.
actif = resultat[resultat["corpus"] == "actif"].drop(columns="corpus")
archive = resultat[resultat["corpus"] != "actif"].copy()
archive["etat"] = archive["etat"].fillna("non audite")

actif.to_csv("repertoire_codes_zoo.csv", index=False)
archive.to_csv("repertoire_codes_archive.csv", index=False)
print(f"{len(actif)} fichiers du corpus actif, {len(archive)} archives ou absents")
print(actif.head(20).to_string())

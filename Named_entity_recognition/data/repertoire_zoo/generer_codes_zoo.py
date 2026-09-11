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
resultat = resultat.rename(columns={"identifiant": "ancien_code", "statut": "etat"})
resultat = resultat.sort_values("code_zoo")

resultat.to_csv("repertoire_codes_zoo.csv", index=False)
print(f"{len(resultat)} fichiers traites")
print(resultat.head(20).to_string())

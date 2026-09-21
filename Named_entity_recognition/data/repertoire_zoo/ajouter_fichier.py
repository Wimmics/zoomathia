"""
Script pour ajouter facilement un nouvel auteur/oeuvre/fichier au systeme zoo.
Usage: python3 ajouter_fichier.py

Fonctionne entierement a partir des fichiers CSV de ce dossier (auteurs_rows.csv,
oeuvres_rows.csv, fichiers_rows.csv) : plus de base Supabase en ligne, tout est
sur Git. Un nouvel identifiant est calcule comme (le plus grand id existant + 1)
dans le fichier concerne - le meme principe que l'auto-increment d'une base de
donnees, en plus simple.

Attention en equipe : si deux personnes ajoutent un auteur/une oeuvre en meme
temps sans avoir recupere (git pull) les derniers CSV, elles peuvent calculer
le meme "prochain identifiant" et entrer en collision. Fais un git pull juste
avant de lancer ce script.
"""
import csv
import os
import shutil
import subprocess

LANGUE_CODE = {"grec": "g", "latin": "l", "anglais": "e", "francais": "f", "italien": "i"}
DOSSIER = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.expanduser("~/Projets/zoomathia")
DATA_DIR = os.path.join(REPO_DIR, "Named_entity_recognition", "data")

AUTEURS_CSV = os.path.join(DOSSIER, "auteurs_rows.csv")
OEUVRES_CSV = os.path.join(DOSSIER, "oeuvres_rows.csv")
FICHIERS_CSV = os.path.join(DOSSIER, "fichiers_rows.csv")


def lire_csv(chemin):
    with open(chemin, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def ecrire_csv(chemin, lignes, fieldnames):
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(lignes)


def prochain_id(lignes):
    if not lignes:
        return 1
    return max(int(r["id"]) for r in lignes) + 1


def chercher_auteur(auteurs, nom):
    nom_lower = nom.lower()
    return [a for a in auteurs if nom_lower in a["nom_canonique"].lower()]


def creer_auteur(auteurs, nom, identifiant, periode):
    nouvel_id = prochain_id(auteurs)
    ligne = {"id": str(nouvel_id), "nom_canonique": nom, "identifiant": identifiant, "periode": periode}
    auteurs.append(ligne)
    ecrire_csv(AUTEURS_CSV, auteurs, ["id", "nom_canonique", "identifiant", "periode"])
    return nouvel_id


def chercher_oeuvres(oeuvres, auteur_id):
    return [o for o in oeuvres if int(o["auteur_id"]) == auteur_id]


def creer_oeuvre(oeuvres, auteur_id, titre, langue_orig):
    nouvel_id = prochain_id(oeuvres)
    ligne = {
        "id": str(nouvel_id), "auteur_id": str(auteur_id),
        "titre_original": titre, "titre_francais": "", "titre_anglais": "",
        "langue_originale": langue_orig, "dans_classeur_lea": "",
        "original_sur_git": "Oui", "traduction_anglaise_sur_git": "",
        "traduction_francaise_sur_git": "", "traduction_italienne_sur_git": "",
        "note": "",
    }
    oeuvres.append(ligne)
    fieldnames = list(oeuvres[0].keys()) if len(oeuvres) == 1 else [
        "id", "auteur_id", "titre_original", "titre_francais", "titre_anglais",
        "langue_originale", "dans_classeur_lea", "original_sur_git",
        "traduction_anglaise_sur_git", "traduction_francaise_sur_git",
        "traduction_italienne_sur_git", "note",
    ]
    ecrire_csv(OEUVRES_CSV, oeuvres, fieldnames)
    return nouvel_id


def calculer_numero_oeuvre(oeuvres, auteur_id, oeuvre_id):
    oeuvres_auteur = sorted(chercher_oeuvres(oeuvres, auteur_id), key=lambda o: int(o["id"]))
    ids = [int(o["id"]) for o in oeuvres_auteur]
    return ids.index(oeuvre_id) + 1


def ajouter_fichier_csv(fichiers, oeuvre_id, nom_fichier, langue, format_="TEI P5", statut="Disponible", source=""):
    nouvel_id = prochain_id(fichiers)
    ligne = {
        "id": str(nouvel_id), "oeuvre_id": str(oeuvre_id), "nom_fichier": nom_fichier,
        "format": format_, "langue": langue, "statut": statut, "source": source,
    }
    fichiers.append(ligne)
    ecrire_csv(FICHIERS_CSV, fichiers, ["id", "oeuvre_id", "nom_fichier", "format", "langue", "statut", "source"])
    return nouvel_id


def calculer_rang_fichier(fichiers, oeuvre_id, langue):
    memes = [f for f in fichiers if int(f["oeuvre_id"]) == oeuvre_id and f["langue"] == langue]
    memes = sorted(memes, key=lambda f: int(f["id"]))
    return len(memes)  # le fichier qu'on vient d'ajouter est deja dans la liste -> son rang = position finale


def main():
    print("=== Ajout d'un nouveau fichier au systeme zoo ===\n")

    auteurs = lire_csv(AUTEURS_CSV)
    oeuvres = lire_csv(OEUVRES_CSV)
    fichiers = lire_csv(FICHIERS_CSV)

    nom_auteur = input("Nom de l'auteur (ex: ARISTOTELES): ").strip().upper()
    resultats = chercher_auteur(auteurs, nom_auteur)

    if resultats:
        print("\nAuteur(s) trouve(s):")
        for r in resultats:
            print(f"  id={r['id']}: {r['nom_canonique']}")
        auteur_id = int(input("Choisis l'id de l'auteur (ou tape 'nouveau' pour en creer un): ") or 0)
    else:
        print("Aucun auteur trouve.")
        auteur_id = 0

    if not auteur_id:
        identifiant = input("Identifiant existant (tlg0086, viaf..., ou vide): ").strip()
        periode = input("Periode (antique/tardo-antique/medieval): ").strip()
        auteur_id = creer_auteur(auteurs, nom_auteur, identifiant, periode)
        print(f"Nouvel auteur cree, id={auteur_id}")

    oeuvres_de_l_auteur = chercher_oeuvres(oeuvres, auteur_id)
    if oeuvres_de_l_auteur:
        print("\nOeuvres existantes pour cet auteur:")
        for o in oeuvres_de_l_auteur:
            print(f"  id={o['id']}: {o['titre_original']} ({o['langue_originale']})")
    oeuvre_id_input = input("\nId de l'oeuvre existante (ou vide pour en creer une nouvelle): ").strip()

    if not oeuvre_id_input:
        titre = input("Titre original de l'oeuvre: ").strip()
        langue_orig = input("Langue originale (grec/latin): ").strip()
        oeuvre_id = creer_oeuvre(oeuvres, auteur_id, titre, langue_orig)
        print(f"Nouvelle oeuvre creee, id={oeuvre_id}")
    else:
        oeuvre_id = int(oeuvre_id_input)

    nom_fichier = input("\nNom du fichier (ex: mon_texte_tei.xml): ").strip()
    langue = input("Langue de ce fichier (grec/latin/anglais/francais/italien): ").strip()
    source = input("Source (Perseus, First1KGreek, etc., optionnel): ").strip()

    ajouter_fichier_csv(fichiers, oeuvre_id, nom_fichier, langue, source=source)
    print("\nFichier ajoute a fichiers_rows.csv.")

    numero_oeuvre = calculer_numero_oeuvre(oeuvres, auteur_id, oeuvre_id)
    lettre = LANGUE_CODE.get(langue, "?")
    rang = calculer_rang_fichier(fichiers, oeuvre_id, langue)
    suffixe = "" if rang == 1 else f"_{rang}"
    code_zoo = f"zoo{auteur_id}/{numero_oeuvre}{lettre}{suffixe}"
    print(f"Code zoo attribue: {code_zoo}")

    dossier_cible = os.path.join(DATA_DIR, "zoo", f"zoo{auteur_id}")
    os.makedirs(dossier_cible, exist_ok=True)
    chemin_cible = os.path.join(dossier_cible, f"{numero_oeuvre}{lettre}{suffixe}.xml")

    print("\nRegeneration de repertoire_codes_zoo.csv...")
    subprocess.run(["python3", "generer_codes_zoo.py"], cwd=DOSSIER, check=True)

    chemin_source = input(f"\nChemin complet du fichier a placer (ou vide pour le faire manuellement): ").strip()
    if chemin_source and os.path.exists(chemin_source):
        shutil.copy(chemin_source, chemin_cible)
        print(f"Fichier copie vers: {chemin_cible}")
        proposer_commit_et_push(code_zoo, nom_auteur, oeuvres, oeuvre_id, langue, chemin_cible)
    else:
        print(f"Pense a placer le fichier manuellement vers: {chemin_cible}")
        reponse = input("Fichier place ? Lancer git add/commit maintenant ? (o/n) ").strip().lower()
        if reponse == "o":
            proposer_commit_et_push(code_zoo, nom_auteur, oeuvres, oeuvre_id, langue, chemin_cible)


def proposer_commit_et_push(code_zoo, nom_auteur, oeuvres, oeuvre_id, langue, chemin_fichier):
    """Fait git add + git commit (message genere automatiquement) sur le
    fichier ajoute et sur les CSV mis a jour, puis propose (avec
    confirmation) de faire git push."""
    titre = next((o["titre_original"] for o in oeuvres if int(o["id"]) == oeuvre_id), "")
    message = (
        f"Ajoute {code_zoo} ({nom_auteur}, {titre}) - temoin {langue}\n\n"
        f"Fichier : {os.path.relpath(chemin_fichier, REPO_DIR)}"
    )

    subprocess.run(["git", "add", chemin_fichier], cwd=REPO_DIR, check=True)
    subprocess.run(["git", "add", AUTEURS_CSV, OEUVRES_CSV, FICHIERS_CSV,
                     os.path.join(DOSSIER, "repertoire_codes_zoo.csv"),
                     os.path.join(DOSSIER, "repertoire_codes_archive.csv")], cwd=REPO_DIR, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=REPO_DIR, check=True)
    print(f"\nCommit effectue :\n{message}\n")

    reponse = input("Faire 'git push' maintenant ? (o/n) ").strip().lower()
    if reponse == "o":
        subprocess.run(["git", "push"], cwd=REPO_DIR, check=True)
        print("Pousse sur le depot distant.")
    else:
        print("Commit local uniquement, pas de push. Tu peux le faire toi-meme plus tard.")


if __name__ == "__main__":
    main()

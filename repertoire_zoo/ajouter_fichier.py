"""
Script pour ajouter facilement un nouvel auteur/oeuvre/fichier au systeme zoo.
Usage: python3 ajouter_fichier.py
"""
import os
import shutil
from supabase import create_client

sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

LANGUE_CODE = {"grec": "g", "latin": "l", "anglais": "e", "francais": "f", "italien": "i"}
DATA_DIR = os.path.expanduser("~/Projets/zoomathia/Named_entity_recognition/data")

def chercher_auteur(nom):
    res = sb.table("auteurs").select("id, nom_canonique").ilike("nom_canonique", f"%{nom}%").execute()
    return res.data

def creer_auteur(nom, identifiant, periode):
    res = sb.table("auteurs").insert({
        "nom_canonique": nom, "identifiant": identifiant, "periode": periode
    }).execute()
    return res.data[0]["id"]

def chercher_oeuvres(auteur_id):
    res = sb.table("oeuvres").select("id, titre_original, langue_originale").eq("auteur_id", auteur_id).execute()
    return res.data

def creer_oeuvre(auteur_id, titre, langue_orig):
    res = sb.table("oeuvres").insert({
        "auteur_id": auteur_id, "titre_original": titre, "langue_originale": langue_orig
    }).execute()
    return res.data[0]["id"]

def calculer_numero_oeuvre(auteur_id, oeuvre_id):
    res = sb.table("oeuvres").select("id").eq("auteur_id", auteur_id).order("id").execute()
    ids = [r["id"] for r in res.data]
    return ids.index(oeuvre_id) + 1

def ajouter_fichier(oeuvre_id, nom_fichier, langue, format_="TEI P5", statut="Disponible", source=""):
    sb.table("fichiers").insert({
        "oeuvre_id": oeuvre_id, "nom_fichier": nom_fichier, "format": format_,
        "langue": langue, "statut": statut, "source": source
    }).execute()

def main():
    print("=== Ajout d'un nouveau fichier au systeme zoo ===\n")

    nom_auteur = input("Nom de l'auteur (ex: ARISTOTELES): ").strip().upper()
    resultats = chercher_auteur(nom_auteur)

    if resultats:
        print(f"\nAuteur(s) trouve(s):")
        for r in resultats:
            print(f"  id={r['id']}: {r['nom_canonique']}")
        auteur_id = int(input("Choisis l'id de l'auteur (ou tape 'nouveau' pour en creer un): ") or 0)
    else:
        print("Aucun auteur trouve.")
        auteur_id = 0

    if not auteur_id:
        identifiant = input("Identifiant existant (tlg0086, viaf..., ou vide): ").strip()
        periode = input("Periode (antique/tardo-antique/medieval): ").strip()
        auteur_id = creer_auteur(nom_auteur, identifiant, periode)
        print(f"Nouvel auteur cree, id={auteur_id}")

    oeuvres = chercher_oeuvres(auteur_id)
    if oeuvres:
        print(f"\nOeuvres existantes pour cet auteur:")
        for o in oeuvres:
            print(f"  id={o['id']}: {o['titre_original']} ({o['langue_originale']})")
    oeuvre_id = input("\nId de l'oeuvre existante (ou vide pour en creer une nouvelle): ").strip()

    if not oeuvre_id:
        titre = input("Titre original de l'oeuvre: ").strip()
        langue_orig = input("Langue originale (grec/latin): ").strip()
        oeuvre_id = creer_oeuvre(auteur_id, titre, langue_orig)
        print(f"Nouvelle oeuvre creee, id={oeuvre_id}")
    else:
        oeuvre_id = int(oeuvre_id)

    nom_fichier = input("\nNom du fichier (ex: mon_texte_tei.xml): ").strip()
    langue = input("Langue de ce fichier (grec/latin/anglais/francais/italien): ").strip()
    source = input("Source (Perseus, First1KGreek, etc., optionnel): ").strip()

    ajouter_fichier(oeuvre_id, nom_fichier, langue, source=source)
    print(f"\nFichier ajoute a Supabase.")

    numero_oeuvre = calculer_numero_oeuvre(auteur_id, oeuvre_id)
    lettre = LANGUE_CODE.get(langue, "?")
    code_zoo = f"zoo{auteur_id}/{numero_oeuvre}{lettre}"
    print(f"Code zoo attribue: {code_zoo}")

    dossier_cible = os.path.join(DATA_DIR, "zoo", f"zoo{auteur_id}")
    os.makedirs(dossier_cible, exist_ok=True)
    chemin_cible = os.path.join(dossier_cible, f"{numero_oeuvre}{lettre}.xml")

    if os.path.exists(chemin_cible):
        suffixe = 2
        while os.path.exists(os.path.join(dossier_cible, f"{numero_oeuvre}{lettre}_{suffixe}.xml")):
            suffixe += 1
        chemin_cible = os.path.join(dossier_cible, f"{numero_oeuvre}{lettre}_{suffixe}.xml")
        code_zoo = f"zoo{auteur_id}/{numero_oeuvre}{lettre}_{suffixe}"
        print(f"Un fichier existe deja a {numero_oeuvre}{lettre}.xml, ce nouveau temoin devient: {code_zoo}")

    chemin_source = input(f"\nChemin complet du fichier a placer (ou vide pour le faire manuellement): ").strip()
    if chemin_source and os.path.exists(chemin_source):
        shutil.copy(chemin_source, chemin_cible)
        print(f"Fichier copie vers: {chemin_cible}")
        print("N'oublie pas de faire 'git add' dessus ensuite.")
    else:
        print(f"Pense a placer le fichier manuellement vers: {chemin_cible}")

if __name__ == "__main__":
    main()

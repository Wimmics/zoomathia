#!/usr/bin/env python3
"""
migrate_to_supabase.py (version securisee)

Migre les tables Auteurs/Oeuvres/Fichiers de la base SQLite locale
(zoomathia_final.db) vers la base PostgreSQL de production sur Supabase.

ATTENTION : ce script fait un DROP TABLE CASCADE puis recree les tables
sur Supabase -- toute donnee presente uniquement sur Supabase (jamais
redescendue en SQLite) sera perdue. Verifier avant de lancer que
zoomathia_final.db est bien a jour (cf. les mises a jour faites en
session -- notes Semonide/Phedre, statuts de fichiers).

Le mot de passe Supabase n'est plus stocke en clair dans ce fichier :
il est lu depuis la variable d'environnement SUPABASE_DB_PASSWORD.

USAGE:
    export SUPABASE_DB_PASSWORD='votre_mot_de_passe'
    python3 migrate_to_supabase.py
"""
import os
import sys
import sqlite3

try:
    import psycopg2
except ImportError:
    sys.exit("Ce script necessite psycopg2. Installer avec : pip install psycopg2-binary --break-system-packages")

SUPABASE_HOST = "db.gfzqaglbnoqfwkgolvgh.supabase.co"
SUPABASE_PORT = 5432
SUPABASE_USER = "postgres"
SUPABASE_DBNAME = "postgres"

mot_de_passe = os.environ.get("SUPABASE_DB_PASSWORD")
if not mot_de_passe:
    sys.exit(
        "Variable d'environnement SUPABASE_DB_PASSWORD non definie.\n"
        "Executer d'abord : export SUPABASE_DB_PASSWORD='votre_mot_de_passe'"
    )

PG_URL = f"postgresql://{SUPABASE_USER}:{mot_de_passe}@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DBNAME}"

# Connexion SQLite
sqlite_conn = sqlite3.connect('zoomathia_final.db')
sqlite_cursor = sqlite_conn.cursor()

# Connexion Supabase
pg_conn = psycopg2.connect(PG_URL)
pg_cursor = pg_conn.cursor()

print("Connexions etablies (SQLite local + Supabase).")

reponse = input(
    "\nATTENTION : ceci va DROP puis RECREER les tables auteurs/oeuvres/fichiers "
    "sur Supabase, a partir du contenu de zoomathia_final.db.\n"
    "Toute donnee modifiee UNIQUEMENT sur Supabase (pas dans le SQLite local) sera perdue.\n"
    "Continuer ? [oui/N] "
)
if reponse.strip().lower() != "oui":
    print("Annule.")
    sys.exit(0)

# Creer les tables PostgreSQL
pg_cursor.execute('DROP TABLE IF EXISTS fichiers CASCADE;')
pg_cursor.execute('DROP TABLE IF EXISTS oeuvres CASCADE;')
pg_cursor.execute('DROP TABLE IF EXISTS auteurs CASCADE;')

pg_cursor.execute('''
    CREATE TABLE auteurs (
        id SERIAL PRIMARY KEY,
        nom_canonique TEXT NOT NULL,
        identifiant TEXT UNIQUE NOT NULL,
        periode TEXT
    );
''')

pg_cursor.execute('''
    CREATE TABLE oeuvres (
        id SERIAL PRIMARY KEY,
        auteur_id INTEGER NOT NULL REFERENCES auteurs(id),
        titre_original TEXT,
        titre_francais TEXT,
        titre_anglais TEXT,
        langue_originale TEXT,
        dans_classeur_lea TEXT DEFAULT 'Non',
        original_sur_git TEXT DEFAULT 'Non',
        traduction_anglaise_sur_git TEXT DEFAULT 'Non',
        traduction_francaise_sur_git TEXT DEFAULT 'Non',
        traduction_italienne_sur_git TEXT DEFAULT 'Non',
        note TEXT
    );
''')

pg_cursor.execute('''
    CREATE TABLE fichiers (
        id SERIAL PRIMARY KEY,
        oeuvre_id INTEGER NOT NULL REFERENCES oeuvres(id),
        nom_fichier TEXT NOT NULL,
        format TEXT,
        langue TEXT,
        statut TEXT,
        source TEXT
    );
''')

pg_conn.commit()
print("Tables recreees sur Supabase.")

# Migration Auteurs
sqlite_cursor.execute("SELECT id, nom_canonique, identifiant, periode FROM Auteurs")
auteurs = sqlite_cursor.fetchall()
for a in auteurs:
    pg_cursor.execute(
        "INSERT INTO auteurs (id, nom_canonique, identifiant, periode) VALUES (%s, %s, %s, %s)",
        a
    )
pg_cursor.execute("SELECT setval('auteurs_id_seq', (SELECT MAX(id) FROM auteurs))")
print(f"{len(auteurs)} auteur(s) migre(s).")

# Migration Oeuvres
sqlite_cursor.execute("""
    SELECT id, auteur_id, titre_original, titre_francais, titre_anglais, langue_originale,
           dans_classeur_lea, original_sur_git, traduction_anglaise_sur_git,
           traduction_francaise_sur_git, traduction_italienne_sur_git, note
    FROM Oeuvres
""")
oeuvres = sqlite_cursor.fetchall()
for o in oeuvres:
    pg_cursor.execute("""
        INSERT INTO oeuvres (id, auteur_id, titre_original, titre_francais, titre_anglais,
                              langue_originale, dans_classeur_lea, original_sur_git,
                              traduction_anglaise_sur_git, traduction_francaise_sur_git,
                              traduction_italienne_sur_git, note)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, o)
pg_cursor.execute("SELECT setval('oeuvres_id_seq', (SELECT MAX(id) FROM oeuvres))")
print(f"{len(oeuvres)} oeuvre(s) migree(s).")

# Migration Fichiers
sqlite_cursor.execute("SELECT id, oeuvre_id, nom_fichier, format, langue, statut, source FROM Fichiers")
fichiers = sqlite_cursor.fetchall()
for f in fichiers:
    pg_cursor.execute(
        "INSERT INTO fichiers (id, oeuvre_id, nom_fichier, format, langue, statut, source) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)", f
    )
pg_cursor.execute("SELECT setval('fichiers_id_seq', (SELECT MAX(id) FROM fichiers))")
print(f"{len(fichiers)} fichier(s) migre(s).")

pg_conn.commit()
print("\nMigration terminee et validee.")

sqlite_conn.close()
pg_conn.close()

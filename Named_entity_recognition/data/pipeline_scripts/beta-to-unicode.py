import xml.etree.ElementTree as ET
from beta_code import beta_code_to_greek
import glob

def convert_xml_betacode_to_unicode(input_file, output_file):
    """
    Lit un fichier XML, identifie les zones de texte en Beta-code,
    les convertit en Grec Unicode, et sauvegarde le nouveau fichier XML.
    """
    try:
        # 1. Enregistrer le préfixe de namespace si le XML en utilise un
        # (Pour éviter que ElementTree n'ajoute des "ns0:" partout lors de la sauvegarde)
        ET.register_namespace('', "http://www.tei-c.org/ns/1.0")

        # 2. Charger et parser le fichier XML
        tree = ET.parse(input_file)
        root = tree.getroot()

        # 3. Fonction récursive pour parcourir et convertir tous les nœuds de texte
        def traverse_and_convert(element):
            # Convertir le texte contenu dans la balise (ex: <l>TEXTE</l>)
            if element.text and element.text.strip():
                # On ne convertit que si on suppose que c'est du beta-code (grec)
                # Note: Dans un vrai pipeline, on vérifie souvent l'attribut lang="grc"
                # ou on exclut les balises d'en-tête (teiHeader) qui sont souvent en anglais.
                # Ici on applique une conversion de base.
                element.text = safe_convert(element.text)

            # Convertir le texte de queue (ex: <l>...</l> TEXTE_DE_QUEUE <l>...</l>)
            if element.tail and element.tail.strip():
                element.tail = safe_convert(element.tail)

            # Parcourir les enfants
            for child in element:
                traverse_and_convert(child)

        # 4. Fonction d'aide pour isoler la logique de conversion
        def safe_convert(text):
            # Le beta-code utilise souvent des conventions spécifiques.
            # Le module s'attend à du beta-code classique.
            try:
                # Conversion du beta code à l'unicode
                converted_text = beta_code_to_greek(text)
                return converted_text
            except Exception as e:
                print(f"Erreur lors de la conversion de la chaîne: '{text[:20]}...' - {e}")
                return text

        # 5. On applique la fonction récursive mais idéalement SEULEMENT au corps du texte
        # pour éviter de convertir l'anglais du <teiHeader> en lettres grecques aléatoires.
        # Recherche de la balise <body> ou <text> selon le standard TEI.
        text_body = root.find('.//body')
        if text_body is None:
            text_body = root.find('.//text')

        if text_body is not None:
            traverse_and_convert(text_body)
            print("Conversion appliquée au contenu du texte.")
        else:
            print("Attention : Balise <body> ou <text> non trouvée, application à tout le document.")
            traverse_and_convert(root)

        # 6. Sauvegarder l'arbre XML modifié
        # On spécifie l'encodage utf-8 et la déclaration xml
        tree.write(output_file, encoding="utf-8", xml_declaration=True)
        print(f"Fichier converti avec succès : {output_file}")

    except ET.ParseError:
        print(f"Erreur : Le fichier {input_file} n'est pas un XML valide.")
    except Exception as e:
        print(f"Une erreur inattendue s'est produite : {e}")


# --- Utilisation du script ---
if __name__ == "__main__":
    files = glob.glob("*.xml")
    for file in files:
        fichier_entree = file
        fichier_sortie = f"{file}_unicode.xml"

        convert_xml_betacode_to_unicode(fichier_entree, fichier_sortie)
import os
from lxml import etree

def apply_xslt_to_folder(folder_path, xsl_path):
    # Parser et préparer la feuille de style XSLT
    try:
        xslt_doc = etree.parse(xsl_path)
        transform = etree.XSLT(xslt_doc)
    except Exception as e:
        print(f"Erreur lors du chargement du fichier XSL : {e}")
        return

    # os.walk parcourt l'arborescence complète (dossiers et sous-dossiers)
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.xml'):
                file_path = os.path.join(root, file)
                print(f"Transformation de : {file_path}")
                
                try:
                    # Lecture du fichier XML d'origine
                    xml_doc = etree.parse(file_path)
                    file_root = xml_doc.getroot()

                    if file_root.tag == '{http://www.tei-c.org/ns/1.0}TEI':
                        print(f"Ignored (already in TEI P5 version) : {file_path}")
                        continue
                    # Application de la transformation
                    result_tree = transform(xml_doc)
                    
                    # Écriture du résultat en écrasant le fichier d'origine
                    # pretty_print conserve l'indentation et xml_declaration ajoute l'en-tête XML
                    with open(file_path, 'wb') as f:
                        f.write(etree.tostring(
                            result_tree, 
                            pretty_print=True, 
                            xml_declaration=True, 
                            encoding='UTF-8'
                        ))
                        
                except Exception as e:
                    print(f"Erreur sur le fichier {file} : {e}")


if __name__ == "__main__":
    # Définissez ici le nom de votre fichier XSL
    feuille_style = "TEI-P5/p4top5.xsl"
    dossier_textes = "../data_translated/"
    
    apply_xslt_to_folder(dossier_textes, feuille_style)
    print("Processus de transformation terminé.")
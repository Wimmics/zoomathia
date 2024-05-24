import os

from Named_entity_recognition.extraction_step import annotate_texts
from Named_entity_recognition.translation_step import main_translation
from Named_entity_recognition.translation_to_csv_step import main_transformation_to_csv

# Obtenez le chemin du répertoire du script
repertoire_script = os.path.dirname(os.path.abspath(__file__))
nom_dossier = "tlg0627"

# path for the original data
original_data = os.path.join(repertoire_script, "data/original_files/" + nom_dossier)

# Spécifiez le chemin du dossier de traduction
translated_data_path = os.path.join(repertoire_script, "data/translated_files/")
print("path for translation: ", translated_data_path)
target_directory_path = translated_data_path + nom_dossier

# Spécifiez le chemin du dossier de l'extraction
extracted_data_path = os.path.join(repertoire_script, "data/extraction_result/")
print("path for translation: ", extracted_data_path)
extracted_directory_path = extracted_data_path + nom_dossier

# Spécifiez le chemin du dossier de la transformation
#final_data_path = os.path.join(repertoire_script, "data/csv_result/")
#print("path for translation: ", final_data_path)
#final_directory_path = final_data_path + nom_dossier


def chek_exists_directory(directory_path):  # Vérifiez si le dossier n'existe pas déjà
    try:
        if not os.path.exists(directory_path):
            # Créez le dossier
            os.makedirs(directory_path)
            print(f"Le dossier '{directory_path}' a été créé avec succès.")
        else:
            print(f"Le dossier '{directory_path}' existe déjà.")
    except FileExistsError:
        print(f"Le dossier '{directory_path}' existe déjà.")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")


chek_exists_directory(target_directory_path)
chek_exists_directory(extracted_directory_path)
#chek_exists_directory(final_directory_path)

#original_directory_path = original_data
#files = os.listdir(original_directory_path)
#print(files)
#file_name_tobe_delete = ".DS_Store"

#if file_name_tobe_delete in files:
 #   files.remove(".DS_Store")

#main_translation(files, original_directory_path, target_directory_path)
#print("files_translated")

# List all files in the directory
files_translated = os.listdir(target_directory_path)
print(files_translated)
file_name_tobe_delete = ".DS_Store"

#if file_name_tobe_delete in files:

 #   files.remove(".DS_Store")
annotate_texts(target_directory_path, extracted_directory_path)

files_extracted = os.listdir(extracted_directory_path)
print(files_extracted)
file_name_tobe_delete = ".DS_Store"
#if file_name_tobe_delete in files:
 #   files.remove(".DS_Store")

#main_transformation_to_csv(files_extracted, extracted_directory_path, final_directory_path,"chapter")#poem, section", chapter)

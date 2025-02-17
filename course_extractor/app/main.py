import os

from AutoRevise.course_extractor.app.db.models import CourseDocument
from AutoRevise.course_extractor.app.extractors.pdf_extractor import extract_text_from_pdf, download_pdf
from AutoRevise.course_extractor.app.storage.mongodb_storage import save_courses_to_mongodb


# Liste des URLs des PDFs à traiter
urls = [
    "https://urfist.pages.math.unistra.fr/cours-python/cours-python.pdf",
    "https://xgarrido.github.io/licence_python_teaching/pdf/01_slide_environnement.pdf",
    "https://xgarrido.github.io/licence_python_teaching/pdf/02_slide_type.pdf",
    "https://xgarrido.github.io/licence_python_teaching/pdf/03_slide_fonction.pdf",
    "https://xgarrido.github.io/licence_python_teaching/pdf/04_slide_module.pdf"
]

# Dossier de téléchargement
download_dir = "downloads"
documents = []  # Liste des documents à insérer

for url in urls:
    # Télécharger le PDF
    downloaded_pdf_path = download_pdf(url, download_dir)

    # Vérifier si le fichier a bien été téléchargé
    if not os.path.exists(downloaded_pdf_path):
        print(f"Échec du téléchargement pour {url}")
        continue

    # Extraire le texte du PDF
    text = extract_text_from_pdf(downloaded_pdf_path)

    # Déterminer le nom du fichier
    file_name = os.path.basename(url)

    # Métadonnées associées
    metadata = {
        "title": f"Document extrait de {file_name}",
        "source": url
    }

    # Contenu du document
    content = {
        "text": text
    }

    tags = ["python", "programming"]

    # Créer un objet CourseDocument et l'ajouter à la liste
    course_doc = CourseDocument(file_name, "pdf", metadata, content, tags)
    documents.append(course_doc)

# Insérer tous les documents en une seule opération
if documents:
    inserted_ids = save_courses_to_mongodb(documents)
    print(f"{len(inserted_ids)} documents insérés avec succès.")
else:
    print("Aucun document à insérer.")

import fitz  # PyMuPDF

def extract_text_and_images_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    images = []
    for i, page in enumerate(doc):
        text += page.get_text()
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            images.append(base_image["image"])
    return text, images
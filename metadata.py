from PIL import Image
from PyPDF2 import PdfReader
import os


def extract_image_metadata(filepath):

    try:
        image = Image.open(filepath)

        metadata = {}

        metadata["Filename"] = os.path.basename(filepath)
        metadata["Format"] = image.format
        metadata["Mode"] = image.mode
        metadata["Size"] = image.size

        exif = image.getexif()

        if exif:

            for tag_id, value in exif.items():
                metadata[str(tag_id)] = str(value)

        return metadata

    except Exception as e:

        return {"Error": str(e)}


def extract_pdf_metadata(filepath):

    try:

        reader = PdfReader(filepath)

        metadata = {}

        if reader.metadata:

            for key, value in reader.metadata.items():

                metadata[str(key)] = str(value)

        return metadata

    except Exception as e:

        return {"Error": str(e)}
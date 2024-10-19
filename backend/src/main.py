import binascii
import os
import hashlib
import io
import shutil
import pip

from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn

import pytesseract
import cv2
from PIL import Image
from lingua import Language, LanguageDetectorBuilder

try:
    import spacy
    import en_core_web_lg
except Exception as e:
    match e.args:
        case ("No module named 'en_core_web_lg'",):
            spacy.cli.download("en_core_web_lg")
try:
    import es_core_news_lg
except Exception as e:
    match e.args:
        case ("No module named 'es_core_news_lg'",):
            spacy.cli.download("es_core_news_lg")


from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_image_redactor import ImageRedactorEngine
from presidio_image_redactor import ImageAnalyzerEngine

from pdf2image import convert_from_bytes
import img2pdf

from pathlib import Path

analyzer = AnalyzerEngine(supported_languages=["en", "es"])
anonymizer = AnonymizerEngine()

image_analyzer_engine = ImageAnalyzerEngine(analyzer_engine=analyzer)
image_redactor_engine = ImageRedactorEngine()

app = FastAPI()

origins = [
    "http://0.0.0.0:3000/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _setup_lang_detection():
    languages = [Language.ENGLISH, Language.SPANISH]
    detector = LanguageDetectorBuilder.from_languages(*languages).build()
    return detector

STORAGE_PATH = ""
match os.path.sys.platform:
    case 'linux':
        STORAGE_PATH = Path("/var/tmp/ocultar/").absolute()
    case 'windows':
        STORAGE_PATH = Path("C:\\Temp\\Ocultar\\").absolute()
    case _:
        import sys
        print("Unsupported platform")
        sys.exit(127)

try:
    os.mkdir(STORAGE_PATH)
except FileExistsError:
    pass

detector = _setup_lang_detection()

import time

class RedactFile:
    def get_redacted_filename(filename: str, extension: str | None, or_extension: str) -> str:
        redacted_file_name = filename + ".redacted." + (extension or or_extension)
        return redacted_file_name

    def get_filename_hash(filename: str) -> str:
        hash_object = hashlib.sha256()
        hash_object.update(f"{filename}{time.time_ns()}".encode("utf-8"))
        return hash_object.hexdigest()

    def anonymize_text(file: UploadFile):
        contents = bytes.decode(file.file.read(), encoding="utf-8")
        language = this.detect_text_language(contents)
        if language is not None and language in SUPPORTED_LANGUAGES:
            analyzer_results = analyzer.anonymize(text=contents, language=language)
            anonymized_content = anonymizer.anonymize(text=contents, analyzer_results=analyzer_results)
        return anonymized_content

    def detect_text_language(text: str) -> str | None:
        language = detector.detect_language_of(text)
        language_code = language.iso_code_639_1.name.lower()
        return language_code if language_code in SUPPORTED_LANGUAGES else None

    def write_text(anonymized_text: str, redacted_file_path: str) -> str:
        with open(redacted_file_path, "w") as redacted_text_file:
            redacted_text_file.write(anonymized_results.text)

    def redact_image(file: UploadFile, redacted_file_path: str) -> str:
        content = io.BytesIO(file.file.read())
        original_image = Image.open(content)
        print(redacted_file_path)
        original_image.save(redacted_file_path)
        preprocessed_image = cv2.imread(redacted_file_path)
        #convert to grayscale image
        gray=cv2.cvtColor(preprocessed_image, cv2.COLOR_BGR2GRAY)
        
        # Threshold and blurring for pre-processing. Needed for accuracy in text detection.
        cv2.threshold(gray, 0,255,cv2.THRESH_BINARY| cv2.THRESH_OTSU)[1]
        cv2.medianBlur(gray, 3)
        cv2.imwrite(redacted_file_path, gray)

        text = pytesseract.image_to_string(Image.open(redacted_file_path))
        language = RedactFile.detect_text_language(text=text)
        os.remove(redacted_file_path)

        redacted_image = image_redactor_engine.redact(original_image, (0, 0, 0), language=language)
        redacted_image.save(Path(redacted_file_path).absolute())

    def send_file(original_file_name: str, redacted_file_path: str, media_type: str) -> FileResponse:
        return FileResponse(redacted_file_path, media_type="text/plain", filename=original_file_name)
    """
    def return_extension(content_type: str) -> str:
        match content_type:
            case "image/jpeg":
                return "jpg"
            case "image/png":
                return "png"
            case "image/gif":
                return "gif"
            case "application/pdf":
                return "pdf"
            case "text/plain":
                return "txt"
    """

SUPPORTED_EXTENSIONS = ("jpeg", "jpg", "png", "gif", "pdf", "txt")
SUPPORTED_LANGUAGES = ("en", "es")

@app.post("/upload")
async def upload(file: UploadFile) -> FileResponse:
    file_name_split = file.filename.split(".")
    original_filename = "".join(file_name_split[:-1])
    extension = file_name_split[-1] if file_name_split[-1] in SUPPORTED_EXTENSIONS else None
    mime = file.content_type
    redacted_file_name_hash = RedactFile.get_filename_hash(original_filename)
    redacted_file_name = RedactFile.get_redacted_filename(redacted_file_name_hash, extension=extension, or_extension=file.content_type.split("/")[-1])
    redacted_file_path = Path(os.path.join(STORAGE_PATH, redacted_file_name)).absolute()
    match file.content_type:
        case "text/plain":
            anonymized_text = RedactFile.anonymize_text(file)
            RedactFile.write_text(anonymized_results.text, redacted_file_path)
            return RedactFile.send_file(original_filename, redacted_file_path, media_type=file.content_type)

        case "image/jpeg" | "image/png" | "image/gif" | "image/svg+xml":
            RedactFile.redact_image(file, redacted_file_path)
            return RedactFile.send_file(original_filename, redacted_file_path, media_type=file.content_type)

        case "application/pdf":
            hashed_directory = Path(os.path.join(STORAGE_PATH, redacted_file_name_hash)).absolute()
            try:
                os.mkdir(hashed_directory)
            except:
                shutil.rmtree(hashed_directory)
                os.mkdir(hashed_directory)

            images = convert_from_bytes(pdf_file=file.file.read(), output_folder=hashed_directory)
            for (index, image) in enumerate(images):
                image_path = Path(os.path.join(hashed_directory, f"{redacted_file_name_hash}-{index}.jpg"))
                original_image = Image.open(image_path)
                original_image.save(image_path)
                preprocessed_image = cv2.imread(image_path)
                
                #convert to grayscale image
                gray=cv2.cvtColor(preprocessed_image, cv2.COLOR_BGR2GRAY)
                
                # Threshold and blurring for pre-processing. Needed for accuracy in text detection.
                cv2.threshold(gray, 0,255,cv2.THRESH_BINARY| cv2.THRESH_OTSU)[1]
                cv2.medianBlur(gray, 3)
                cv2.imwrite(image_path, gray)

                text = pytesseract.image_to_string(Image.open(image_path))
                language = RedactFile.detect_text_language(text=text)
                os.remove(redacted_file_path)

                image_redactor_engine.redact(original_image, (0, 0, 0), language=language).convert("RGB").save((image_path).absolute(), "JPEG")

            for intermediate_file in os.listdir(hashed_directory):
                if intermediate_file.endswith(".ppm"):
                    os.remove(Path(os.path.join(hashed_directory, intermediate_file)).absolute())
            images = [Path(os.path.join(hashed_directory, image)).absolute() for image in os.listdir(hashed_directory)]

            with open(redacted_file_path, "wb") as redacted_file:
                redacted_file.write(img2pdf.convert(images))

            shutil.rmtree(hashed_directory)
            return RedactFile.send_file(original_filename, redacted_file_path, media_type=file.content_type)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
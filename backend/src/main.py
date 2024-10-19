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

from lingua import Language, LanguageDetectorBuilder

try:
    import spacy
    import en_core_web_lg
    import es_core_news_lg 
except Exception as e:
    print(e.args)
    match e.args:
        case ("No module named 'es_core_news_lg'",):
            spacy.cli.download("es_core_news_lg")
        case ("No module named 'en_core_web_lg'",):
            spacy.cli.download("en_core_web_lg")
    import en_core_web_lg
    import es_core_news_lg

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_image_redactor import ImageRedactorEngine
from presidio_image_redactor import ImageAnalyzerEngine

from pdf2image import convert_from_bytes
import img2pdf
from PIL import Image

from pathlib import Path

image_analyzer_engine = ImageAnalyzerEngine()
image_redactor_engine = ImageRedactorEngine()
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

app = FastAPI()

def _setup_middleware():
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

_setup_middleware()

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
try:
    os.mkdir("STORAGE_PATH")
except FileExistsError:
    pass

detector = _setup_lang_detection()

class RedactFile:
    def get_redacted_filename(filename: str, extension: str | None, or_extension: str) -> str:
        redacted_file_name = os.path.join(STORAGE, filename + ".redacted." + (extension or or_extension))

    def get_filename_hash(filename: str) -> str:
        hash_object = hashlib.sha256()
        hash_object.update(filename.encode("utf-8"))
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

    def write_text(anonymized_text: str, redacted_file_name: str) -> str:
        with open(redacted_file_name, "w") as redacted_text_file:
            redacted_text_file.write(anonymized_results.text)

    def redact_image(file: UploadFile) -> str:
        content = io.BytesIO(file.file.read())
        image = Image.open(content)
        redacted_image = image_redactor_engine.redact(image, (0, 0, 0))
        redacted_image.save(redacted_file_name)

    def send_file(original_file_name: str, redacted_file_path: str, media_type: str) -> FileResponse:
        return FileResponse(redacted_file_path, media_type="text/plain", filename=original_file_name)

SUPPORTED_EXTENSIONS = ("jpeg", "jpg", "png", "gif", "pdf", "txt")
SUPPORTED_LANGUAGES = ("en", "es")

@app.post("/upload")
async def upload(file: UploadFile) -> FileResponse:
    file_name_split = file.filename.split(".")
    original_filename = "".join(file_name_split(".")[:-1])
    extension = file_name_split[-1] if file_name_split[-1] in ALLOWED_EXTENSIONS else None
    mime = file.content_type
    redacted_file_name_hash = RedactFile.get_filename_hash(original_filename)
    redacted_file_name = RedactFile.get_redacted_filename(redacted_file_name_hash, extension=extension, or_extension="txt")
    redacted_file_path = Path(STORAGE_PATH + redacted_file_name).absolute()

    match file.content_type:
        case "text/plain":
            anonymized_text = RedactFile.anonymize_text(file)
            RedactFile.write_text(anonymized_results.text, redacted_file_name)
            return RedactFile.send_file(original_filename, redacted_file_name, media_type=file.content_type)

        case "image/jpeg" | "image/png" | "image/gif":
            redact_image(file)
            return RedactFile.send_file(original_filename, redacted_file_name, media_type=file.content_type)

        case "application/pdf":
            hashed_directory = Path(STORAGE + redacted_file_name_hash).absolute()
            try:
                os.mkdir(hashed_directory)
            except:
                shutil.rmtree(hashed_directory)
                os.mkdir(hashed_directory)
            images = convert_from_bytes(pdf_file=file.file.read(), output_folder=hashed_directory)
            for (index, image) in enumerate(images):
                image_redactor_engine.redact(image, (0, 0, 0)).convert("RGB").save(Path(hashed_directory + f"{filename}-{index}.jpg"), "JPEG")
            for file in os.listdir(hashed_directory):
                if file.endswith(".ppm"):
                    os.remove(Path(hashed_directory + file).absolute())

            images = [Path(hashed_directory + file).absolute() for image in os.listdir(hashed_directory)]
            with open(redacted_file_name, "wb") as redacted_file:
                redacted_file.write(img2pdf.convert(images))
            shutil.rmtree(hashed_directory)
            return RedactFile.send_file(original_filename, redacted_file_name, media_type=file.content_type)


if __name__ == "__main__":
    print("API working")
    uvicorn.run(app, host="0.0.0.0", port=8000)
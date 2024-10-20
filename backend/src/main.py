import binascii
import os
import hashlib
import io
import time
import shutil
import enum
from typing import Tuple, Annotated

from fastapi import FastAPI, UploadFile, Depends, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
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

import libmat2.images
import libmat2.pdf

from pdf2image import convert_from_bytes
import img2pdf

from pathlib import Path


class Sensitivity(int, enum.Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2

class Options (BaseModel):
    remove_metadata: bool = True
    sensitivity: Sensitivity = Sensitivity.HIGH
    redaction_color: str = "#000000"

def hex_to_rgb(hex_value):
    # Remove the hash sign if it exists
    hex_value = hex_value.lstrip('#')
    
    # Convert each pair of hex digits to decimal and return as a tuple
    return tuple(int(hex_value[i:i + 2], 16) for i in (0, 2, 4))

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

def post_processing(redacted_file_path):
    os.remove(redacted_file_path)    

class RedactFile:
    def get_redacted_filename(filename: str, extension: str | None, or_extension: str) -> str:
        redacted_file_name = filename + ".redacted." + (extension or or_extension)
        return redacted_file_name

    def get_filename_hash(filename: str) -> str:
        hash_object = hashlib.sha256()
        hash_object.update(f"{filename}{time.time_ns()}".encode("utf-8"))
        return hash_object.hexdigest()

    def anonymize_text(file: UploadFile, sensitivity: Sensitivity):
        contents = bytes.decode(file.file.read(), encoding="utf-8")
        language = self.detect_text_language(contents)
        if language is not None and language in SUPPORTED_LANGUAGES:
            entities = ENTITIES.get(sensitivity)
            analyzer_results = analyzer.analyze(text=contents, language=language, score_threshold=entities.get("score_threshold"), entities=entities.get("entities"))
            anonymized_content = anonymizer.anonymize(text=contents, analyzer_results=analyzer_results)
        return anonymized_content

    def detect_text_language(text: str) -> str:
        language = detector.detect_language_of(text)
        if language:
            language_code = language.iso_code_639_1.name.lower()
            return language_code if language_code in SUPPORTED_LANGUAGES else "en"
        return "en"

    def write_text(anonymized_text: str, redacted_file_path: str) -> str:
        with open(redacted_file_path, "w") as redacted_text_file:
            redacted_text_file.write(anonymized_results.text)

    def redact_image(file: UploadFile, redacted_file_path: str, redaction_color: Tuple[int, int, int] ,sensitivity: Sensitivity) -> str:
        content = io.BytesIO(file.file.read())
        original_image = Image.open(content)
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
        entities = ENTITIES.get(sensitivity)
        redacted_image = image_redactor_engine.redact(original_image, redaction_color, language=language, score_threshold=entities.get("score_threshold"), entities=entities.get("entities"))
        redacted_image.save(Path(redacted_file_path).absolute())

    def send_file(original_file_name: str, redacted_file_path: str, media_type: str, background_tasks: BackgroundTasks) -> FileResponse:
        return FileResponse(redacted_file_path, media_type="text/plain", filename=original_file_name, background=background_tasks)


SUPPORTED_EXTENSIONS = ("jpeg", "jpg", "png", "gif", "pdf", "txt")
SUPPORTED_LANGUAGES = ("en", "es")


ENTITIES = {
    Sensitivity.HIGH: {
        "score_threshold": None,
        "entities": None
    },

    Sensitivity.MEDIUM: {
        "score_threshold": 0.4,
        "entities": [
            "CREDIT_CARD",
            "CRYPTO",
            "EMAIL_ADDRESS",
            "IBAN_CODE",
            "LOCATION",
            "PERSON",
            "PHONE_NUMBER",
            "MEDICAL_LICENSE",
            "IN_PAN",
            "IN_AADHAAR",
            "IN_VEHICLE_REGISTRATION",
            "IN_VOTER",
            "IN_PASSPORT"
        ]
    },

    Sensitivity.LOW: {
        "score_threshold": 0.7,
        "entities": [
            "CREDIT_CARD",
            "CRYPTO",
            "IBAN_CODE",
            "MEDICAL_LICENSE",
            "IN_PAN",
            "IN_AADHAAR",
            "IN_VEHICLE_REGISTRATION",
            "IN_VOTER",
            "IN_PASSPORT"
        ]
    }
}


@app.post("/upload")
async def upload(
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File()],
    options: Options = Depends(),
) -> FileResponse:
    file_name_split = file.filename.split(".")
    original_filename = "".join(file_name_split[:-1])
    extension = file_name_split[-1] if file_name_split[-1] in SUPPORTED_EXTENSIONS else None
    mime = file.content_type
    redacted_file_name_hash = RedactFile.get_filename_hash(original_filename)
    redacted_file_name = RedactFile.get_redacted_filename(redacted_file_name_hash, extension=extension, or_extension=file.content_type.split("/")[-1])
    redacted_file_path = Path(os.path.join(STORAGE_PATH, redacted_file_name)).absolute()
    redaction_color = hex_to_rgb(options.redaction_color) or "#000000"
    background_tasks.add_task(post_processing, redacted_file_path)
    match file.content_type:
        case "text/plain":
            anonymized_text = RedactFile.anonymize_text(file, option.sensitivity)
            RedactFile.write_text(anonymized_results.text, redacted_file_path)

        case "image/jpeg" | "image/png":
            RedactFile.redact_image(file, redacted_file_path, redaction_color=redaction_color, sensitivity=options.sensitivity)

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

                entities = ENTITIES.get(sensitivity)
                image_redactor_engine.redact(original_image, redaction_color, language=language, score_threshold=entities.get("score_threshold"), entities=entities.get("entities")).convert("RGB").save((image_path).absolute(), "JPEG")

            for intermediate_file in os.listdir(hashed_directory):
                if intermediate_file.endswith(".ppm"):
                    os.remove(Path(os.path.join(hashed_directory, intermediate_file)).absolute())
            images = [Path(os.path.join(hashed_directory, image)).absolute() for image in os.listdir(hashed_directory)]

            with open(redacted_file_path, "wb") as redacted_file:
                redacted_file.write(img2pdf.convert(images))

            shutil.rmtree(hashed_directory)
        case _:
            return JSONResponse({"error": f"Unsupported file type for file {file.filename}"})

    if options.remove_metadata:
        match file.content_type:
            case "image/png":
                png_parser = libmat2.images.PNGParser(os.fspath(redacted_file_path))
                png_parser.output_filename = os.fspath(redacted_file_path)
                png_parser.remove_all()
            case "image/jpeg":
                jpg_parser = libmat2.images.JPGParser(os.fspath(redacted_file_path))
                jpg_parser.output_filename = os.fspath(redacted_file_path)
                jpg_parser.remove_all()
            case "image/gif":
                gif_parser = libmat2.images.GIFParser(os.fspath(redacted_file_path))
                gif_parser.output_filename = os.fspath(redacted_file_path)
                gif_parser.remove_all()
            case "image/svg+xml":
                svg_parser = libmat2.images.SVGParser(os.fspath(redacted_file_path))
                svg_parser.output_filename = os.fspath(redacted_file_path)
                svg_parser.remove_all()
            case "application/pdf":
                pdf_parser = libmat2.pdf.PDFParser(os.fspath(redacted_file_path))
                pdf_parser.output_filename = os.fspath(redacted_file_path)
                pdf_parser.remove_all()
    return RedactFile.send_file(original_filename + "." + extension, redacted_file_path, media_type=file.content_type, background_tasks=background_tasks)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
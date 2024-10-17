import binascii
import os
import io
import shutil

from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_image_redactor import ImageRedactorEngine
from pdf2image import convert_from_bytes
import img2pdf

from PIL import Image

image_redactor_engine = ImageRedactorEngine()
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()
app = FastAPI()

origins = [
    "http://0.0.0.0:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload(file: UploadFile) -> FileResponse:
    filename, extension = "".join((file.filename.split(".")[:-1])), file.filename.split(".")[-1]
    mime = file.content_type
    redacted_file_name = os.path.join("./backend/storage", filename + ".redacted." + extension)
    match file.content_type:
        case "text/plain":
            contents = bytes.decode(file.file.read(), encoding="utf-8")
            analyzer_results = analyzer.analyze(text=contents, language="en")
            anonymized_results = anonymizer.anonymize(text=contents, analyzer_results=analyzer_results)
            # anonymized_results = anonymized_results.text.encode("utf-8")
            with open(redacted_file_name, "w") as new_file:
                new_file.write(anonymized_results.text)
            return FileResponse(redacted_file_name, media_type="text/plain")
        case "image/jpeg" | "image/png" | "image/gif":
            print(file.content_type)
            content = io.BytesIO(file.file.read())
            image = Image.open(content)
            redacted_image = image_redactor_engine.redact(image, (0, 0, 0))
            redacted_image.save(redacted_file_name)
            return FileResponse(redacted_file_name, media_type=file.content_type)
        case "application/pdf":
            try:
                os.mkdir(f"./{filename}")
            except:
                shutil.rmtree(f"./{filename}")
                os.mkdir(f"./{filename}")
            images = convert_from_bytes(pdf_file=file.file.read(), output_folder=f"./{filename}")
            for (index, image) in enumerate(images):
                image_redactor_engine.redact(image, (0, 0, 0)).convert("RGB").save(f"./{filename}/{filename}-{index}.jpg", "JPEG")
            for file in os.listdir(f"./{filename}/"):
                if file.endswith(".ppm"):
                    os.remove(f'./{filename}/{file}')
            images = [f"./{filename}/{image}" for image in os.listdir(f"./{filename}/")]
            with open(redacted_file_name, "wb") as redacted_file:
                redacted_file.write(img2pdf.convert(images))
            shutil.rmtree(f"./{filename}")
            return FileResponse(redacted_file_name, media_type="application/pdf")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
# Ocultar

<a href="https://ocultar.vercel.app"><img src="./assets/logo-full.png" style="background-color: #ffffff; padding: 15px" alt="Ocultar Logo"></a>

Ocultar is an offline-first software for redaction of personal information and removal of metadata from digital files for enhanced privacy and prevent unintended disclosure of sensitive information.

# Table of Contents

1. [Why]("#why")
2. [Features]("#features")
    - [Offline usage]("#offline-usage")
    - [Web interface]("#web-interface")
    - [Self-hosting]("#self-hosting")
    - [Multi-lingual redaction]("#multi-lingual-redaction")
    - [Batch processing]("#batch-processing")
    - [Customized redaction]("#customized-redaction")
    - [Integrated metadata removal]("#integrated-metadata-removal")
3. [Philosophy]("#philosophy")
4. [Technologies used]("#technologies-used")
5. [Development]("#development")

## Why?

Sharing of digital files containing sensitive information with metadata has become common due to frictionless connectivity enabled by SaaS applications. These files are processed by multiple servers and can be stored indefinitely or processed for extraction of personal information.

Services such as [**Microsoft Presidio**](https://microsoft.github.io/presidio/) for personal information de-identification and [**MAT2 (Metadata Anonymization Toolkit)**](https://0xacab.org/jvoisin/mat2/) for metadata removal  were created to address these issues.

However, the lack of a web interface for Microsoft Presidio creates hindrance in user adoption and lack of integration of metadata removal along with redaction creates another loophole in ensuring end-user privacy. This is not to be blamed, since they were designed as a framework and library respectively, meant to be used as dependency and framework by other applications.

Ocultar aims to be amiable brainchild of these two services by integration of personal information redaction and metadata removal into an user-friendly interface that can be operated offline, self-hosted or via flagship instance.

Reduction of impact of data breaches and unintended transmission of personal information without impacting user experience is our goal.

## Features

### Offline usage

Ocultar can be used offline by desktop application that bundles the needed API for processing files on their local system. This eliminates reliance on cloud services for processing of information which may potentially infringe on privacy.

The ability to operate it offline is also beneficial for organizations who deal with sensitive information, thus being unable to use online services.

**Supported filetypes:**

Currently, we support processing of the following file formats:

#### Redaction

- Plain text files
- Images - JPEG, PNG
- PDF files

#### Metadata removal

- Images: PNG, JPEG, SVG, GIF
- PDF

### Web interface

Some people wish to use web application rather than installing the desktop application. We provide a flagship instance that allows users to upload files. Useful for people who are not able to self-host or use desktop application.

**Our web interface is configured to delete files after processing for additional privacy.**

### Self-hosting

Ocultar can be self-hosted for maximum control over data transmission in case if usage of flagship instance is not for you. We support containerized deployments via Docker for easier deployment.

### Multi-lingual redaction

Ocultar detects multiple languages that are present in a document with ease and redacts based on the detected languages without manual intervention.

Currently, the system supports redaction for English and Spanish with planned support for other languages and development of custom models and recognizers for Indian languages.

### Batch processing

Ocultar supports batch processing of documents. Upload multiple documents at a go and have it redacted with ease.

### Customized redaction

Ocultar supports tweaking of redaction and sanitization by providing options to configure:

1. Color of redaction for images and PDF. Defaults to black.
2. Sensitivity of redaction: Whether all kinds of information need to be redacted or just the sensitive ones. Defaults to high, redacting all information.
3. Metadata removal: Can be turned on or off. This is enabled by default.

###  Integrated metadata removal

Ocultar adds metadata removal on top of redaction for additional privacy so that quasi-identifiers such as creation date, software version and other sensitive information that are embedded in a file are removed.

## Philosophy

### Minimalism

The primary goal of Ocultar is to attain minimalism in terms of dependencies and functionality. The entire design is centered around minimalism for good user experience for different users.

### Privacy

Privacy is one of the core principles of Ocultar. 

# Technologies used

## Frontend

We have made our frontend responsive, accessible and minimal thanks to these amazing technologies:

1. Alpine.js: Minimal web framework with small build size and high performance than frameworks like React or Next. We have chosen it for its minimalism and performance. Paired up with TypeScript, it provides a great development experience.
2. Bun: Highly performant runtime for JavaScript
3. TailwindCSS and DaisyUI: For the user interface components and design for its minimalism and accessibility.
4. Vite: Faster build system for web applications.

## Backend

1. Microsoft Presidio: The heart of Ocultar, it is the one responsible for redaction of PII from files.
2. FastAPI: API framework that is used for redaction and sanitization.
3. MAT2: The ally of Ocultar, aiding removal of metadata from several types of files.
4. Tesseract: Used for extraction of text from image by preprocessing.
5. Lingua language detector: A Python library used for language detection from images.
6. img2pdf and pdf2image libraries for conversion of images to PDF and PDF to image. Needed for processing images and PDF.

## Desktop

1. Tauri: Cross-platform desktop application framework for creation of minimal, performant and secure applications with a good developer experience thanks to Rust and Bun

The frontend codebase is used in the application with slight modifications for making it compatible with desktop operating systems.

## Deployment and automation

Ocultar uses Docker for easier deployments by containerization.

Our flagship instance is hosted on Azure:
1. Backend is deployed by usage of Azure Container Services
2. Frontend is deployed by usage of Azure App Service

The builds for Tauri application are done via GitHub Actions

# Development

## Project structure

The project is a monorepository containing source code for:
- Frontend
- Backend
- Desktop

## Dependencies

You need to make sure that the following dependencies are available on your system for development:

### Backend

1. Python 3.12 or later
2. Poetry for dependency management
3. Tesseract OCR

### Frontend

1. Bun
2. TypeScript

### Desktop

1. Rust
2. Bun

Make sure to use Docker for frontend and backend.

## Manual development

## Frontend

Run the project locally by development server

``` shell
cd frontend
bun install # Install dependencies
bun run dev # Start development server. Should be accessible at http://localhost:3000/
```

Build the frontend and preview it by

``` shell
bun run build && bun run preview
```

## Backend

Install the dependencies by creating a virtual environment

``` shell
cd backend
poetry env use python3.12 # Assuming python3.12 is a valid executable, change it if needed. Minimum version of Python required for the backend is 3.12
source $(poetry env info --path)/bin/activate # Activate the virtual environment on Linux distrubutions.
poetry install
```

Start the development server by the following command

``` shell
fastapi dev src/main.py
```

This should start the development server at http://0.0.0.0:8000/

## Desktop

Install the needed dependencies

``` shell
cd desktop
bun install
```

Run the development build

```shell
bun run tauri dev
```
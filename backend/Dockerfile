FROM python:3-slim-buster

ENV VIRTUAL_ENV=backend

RUN /var/tmp/ocultar/

RUN python3 -m venv $VIRTUAL_ENV

ENV PATH="/$VIRTUAL_ENV/bin:$PATH"

WORKDIR /backend

COPY requirements.txt .

RUN . ./bin/activate && pip install -r requirements.txt

RUN mkdir ./src

COPY ./src ./src

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

#CMD uvicorn src.main:app --host 0.0.0.0 --port 8000
ENTRYPOINT ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
#CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=80"]
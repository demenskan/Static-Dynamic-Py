FROM python:3-alpine

COPY /src /usr/src/app
WORKDIR /usr/src/app

RUN pip install -r requirements.txt

ENTRYPOINT python api.py
# para correr el contenedor temporalmente:
# docker container run -d -p 8000:8000 -v "${PWD}:/usr/src/app" --name bootcamp bootcamp:v1

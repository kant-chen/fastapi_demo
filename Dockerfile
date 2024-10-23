FROM tiangolo/uvicorn-gunicorn:python3.11-slim

COPY . /home/apps
WORKDIR /home/apps

RUN pip install --upgrade pip  && pip install -r requirements.txt

EXPOSE 8000
CMD uvicorn main:app
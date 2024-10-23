FROM tiangolo/uvicorn-gunicorn:python3.11-slim

COPY ./requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip  && pip install -r /tmp/requirements.txt

COPY . /home/apps
WORKDIR /home/apps

CMD uvicorn --host 0.0.0.0 main:app
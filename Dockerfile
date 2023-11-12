FROM python:3.10

ARG GRADIO_SERVER_PORT=7860
ENV GRADIO_SERVER_PORT=${GRADIO_SERVER_PORT}

WORKDIR /workspace

ADD requirements.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements.txt

FROM python:3.10

ARG GRADIO_SERVER_PORT=7860
ENV GRADIO_SERVER_PORT=${GRADIO_SERVER_PORT}

WORKDIR /workspace

ADD *.py requirements.txt /workspace/

RUN pip install -r /workspace/requirements.txt

CMD ["python", "/workspace/run.py"]

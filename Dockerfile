FROM python:3.10

# mark it with a label, so we can remove dangling images
LABEL cicd="be-on-time"

ARG GRADIO_SERVER_PORT=7860
ENV GRADIO_SERVER_PORT=${GRADIO_SERVER_PORT}

WORKDIR /workspace

ADD *.py requirements.txt /workspace/

RUN pip install --no-cache-dir -r /workspace/requirements.txt

CMD ["python", "/workspace/run.py"]

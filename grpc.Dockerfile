FROM python:3.10.7

WORKDIR /opt/app

RUN pip install poetry

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

RUN apt update && apt install -y netcat
RUN poetry config virtualenvs.create false && poetry install

COPY ./ .
COPY grpc.sh /

CMD ["sh", "/grpc.sh"]
#CMD ["python", "grpc_server.py"]
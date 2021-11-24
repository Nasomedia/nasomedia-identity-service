FROM python:3.9

WORKDIR /app

# Install Poetry
ENV POETRY_VERSION=1.1.11 
RUN pip install "poetry==$POETRY_VERSION"

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./ /app/
COPY ./app /app/app
ENV PYTHONPATH=/app
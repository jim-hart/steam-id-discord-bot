FROM python:3.8-slim as python-base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # poetry:
    POETRY_VERSION=1.0.10 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    # paths
    PROJ_PATH="/app"

ENV PATH="$POETRY_HOME/bin:$PATH"

# stage 1
FROM python-base as setup
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
    && curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python \
    && apt-get remove -y curl \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# stage 2
FROM setup as build
WORKDIR $PROJ_PATH
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-ansi

# stage 3
FROM build as deploy
WORKDIR $PROJ_PATH
COPY . .
CMD ["python", "-m", "steam_id_discord_bot"]


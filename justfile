set dotenv-load := true

# Show help message
[private]
@default:
    just --list

# Install all depends for developing
@install:
    uv pip install -e . --group lint --group test
    pre-commit install

# Run tests
@test:
    pytest tests --cov=pyproject --cov-append --cov-report term-missing -v

# Run pre-commit
@lint:
    pre-commit run --all-files

# Run
@run:
    python3 -m pyproject.main

# Up docker compose
@up:
    docker compose -f docker/docker-compose.yaml --env-file=./config/.env up -d --build

# Down docker compose
@down:
    docker compose -f docker/docker-compose.yaml down

# Rename project
@rename name:
    chmod +x ./rename.sh
    ./rename.sh {{name}}

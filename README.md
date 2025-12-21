<div align="center">

# PyProject

[![python](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![UV](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

</div>

Minimal template for a quick start of a Python project.

## Highlights
- **[Actions](https://github.com/features/actions) workflows** for CI tests and linting
- **[Dependabot](https://docs.github.com/en/code-security/dependabot)** for automated dependency updates
- **[Zizmor](https://docs.zizmor.sh/)** for GitHub Actions security checks
- **[Labeler](https://github.com/actions/labeler)** to auto-apply labels to PRs
- **[Mypy](https://mypy-lang.org/)** for static typing + **[Ruff](https://docs.astral.sh/ruff/)** for lint/format
- **[pre-commit](https://pre-commit.com/)** for local hooks before commits
- **docker-compose** out of the box
- **[structlog](https://www.structlog.org/)** logger included by default
- **[AGENTS.md](https://agents.md )** for blazingly fast development


## Commands

```
just rename aboba      # set the project name across the repo
just install           # install python dependencies via uv
just lint              # run formatting and lint checks
just test              # run tests via pytest with coverage
just run               # run the application
just up                # run the application via docker compose
just down              # stop the application via docker compose
```

## Configuring

```sh
cp config/template.config.yaml config/config.yaml
cp config/template.env config/.env
```

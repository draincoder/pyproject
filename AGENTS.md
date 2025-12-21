## Project Structure

```
config/
docker/
src/
  domain/
  application/
  infrastructure/
  presentation/
tests/
  unit/
  integration/
  e2e/
```

Rules:
- Dependencies flow inward: presentation → application → domain
- `domain` contains only business logic, no external dependencies
- `infrastructure` implements interfaces defined in `application`

---

## Architecture Principles (if applicable)

- Follow Clean Architecture by default
- Depend on abstractions, not concrete implementations
- Extend behavior via composition, not modification
- Keep modules small with a single responsibility

---

## Tooling & Standards (Mandatory)

- Python **3.13**
- Task runner: `just`
- Formatting & linting: **Ruff**
- Type checking: **mypy**
- Testing: **pytest** with coverage
- All code must be **fully type annotated**

Common commands:
```sh
just install
just lint
just test
just run
just up
just down
```

---

## Testing Rules (Mandatory)

- Tests mirror `src/` structure
- Use `unit/`, `integration/`, `e2e/`
- Use **Arrange / Act / Assert** with explicit comments
- Do not add comments in tests except parametrization case descriptions
- Name tests by behavior and expected outcome
- Prefer unit tests; add integration tests when behavior spans layers
- Keep tests deterministic, fast, and isolated from network/IO

---

## Commit & Pull Request Rules

- Use **Conventional Commits** (e.g. `feat: add auth middleware`)
- PRs must include a concise description and motivation

---

## Local Configuration

Before running locally:
```sh
cp config/template.config.yaml config/config.yaml
cp config/template.env config/.env
```

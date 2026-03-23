# Contributing Guidelines

Thank you for interest in contributing to MetricForge Crucible! This document outlines the process for contributing code, documentation, and bug reports.

## Getting Started

### Prerequisites

- Python 3.11+
- Git
- GitHub account

### Development Setup

1. **Fork the repository**

```bash
# Go to https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible
# Click "Fork" button
```

2. **Clone your fork**

```bash
git clone https://github.com/YOUR_USERNAME/MetricForge-Crucible.git
cd MetricForge-Crucible
```

3. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. **Install development dependencies**

```bash
pip install -e ".[dev,providers]"
pre-commit install
```

5. **Create feature branch**

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number
```

## Code Style

### Formatting

We use [Black](https://black.readthedocs.io/) for code formatting.

```bash
black src tests
```

### Linting

We use [Flake8](https://flake8.pycqa.org/) for linting.

```bash
flake8 src tests
```

### Type Hints

Use type hints for function parameters and return types:

```python
def get_provider(name: str, config: Dict[str, Any]) -> DataWarehouseProvider:
    """Get a data warehouse provider by name."""
    ...
```

### Docstrings

Use Python docstrings for modules, classes, and functions:

```python
def validate_connection(self) -> bool:
    """
    Validate connection to the data warehouse.
    
    Returns:
        True if connection is valid, False otherwise.
    """
    ...
```

## Testing

### Unit Tests

Write unit tests for new code. Use pytest:

```bash
pytest tests/ -v
pytest tests/test_specific.py -v  # Run specific test file
pytest tests/test_specific.py::test_function -v  # Run specific test
```

### Coverage

Aim for >80% code coverage:

```bash
pytest --cov=src/metricforge --cov-report=html
# Open htmlcov/index.html to view coverage report
```

### Integration Tests

Mark integration tests with `@pytest.mark.integration`:

```python
@pytest.mark.integration
def test_real_duckdb_connection():
    """Test with actual DuckDB connection."""
    ...
```

Run only integration tests:
```bash
pytest -m integration
```

## Commit Messages

Follow conventional commit format:

```
type(scope): brief description

Longer explanation if needed.

Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `style`: Code style
- `chore`: Build, dependencies, etc.

**Examples:**
```
feat(providers): add new data warehouse provider skeleton
fix(config): handle missing environment variable gracefully
docs(setup): improve DuckDB installation instructions
test(providers): add unit tests for Snowflake provider
```

## Pull Request Process

1. **Before starting**
   - Check existing issues/PRs to avoid duplicates
   - Discuss major changes in an issue first

2. **While working**
   - Keep commits small and logical
   - Write descriptive commit messages
   - Add tests for new functionality
   - Update documentation

3. **Before submitting PR**
   - Run tests: `pytest`
   - Check code style: `black src tests && flake8 src tests`
   - Run type checker: `mypy src`
   - Update CHANGELOG.md

4. **Submit PR**
   - Clear title and description
   - Link related issues (`Fixes #123`)
   - Include any breaking changes
   - Add yourself to contributors list

5. **PR Review**
   - Address feedback and comments
   - Push new commits to the same branch
   - Don't force push during review

## Adding a New Provider

### Data Warehouse Provider

See [Provider Development Guide](docs/PROVIDER_DEVELOPMENT.md#adding-a-data-warehouse-provider) for detailed steps.

Quick checklist:
- [ ] Provider class in `src/metricforge/providers/data_warehouse.py`
- [ ] Registered in `DATA_WAREHOUSE_PROVIDERS`
- [ ] Added to `copier.yml` choices
- [ ] Unit tests in `tests/providers/test_*.py`
- [ ] Example configuration in `examples/`
- [ ] Documentation updates

### Semantic Layer Provider

See [Provider Development Guide](docs/PROVIDER_DEVELOPMENT.md#adding-a-semantic-layer-provider) for detailed steps.

Same checklist as above, but for semantic layer.

## Documentation

### Updating README

The main README is in the repository root. Keep it up-to-date with major changes.

### Adding Documentation Pages

1. Create file in `docs/` directory
2. Add to mkdocs.yml navigation
3. Follow markdown formatting standards
4. Include code examples where relevant

### Building Documentation

```bash
mkdocs serve  # Local preview at http://localhost:8000
mkdocs build  # Generate static site in site/
```

## Reporting Bugs

Use GitHub Issues to report bugs. Include:

1. **Title**: Clear, concise description
2. **Environment**: Python version, OS, provider type
3. **Steps to reproduce**: Minimal reproducible example
4. **Expected behavior**: What should happen
5. **Actual behavior**: What actually happens
6. **Logs/errors**: Full error messages
7. **Configuration**: Relevant metricforge.yaml (without secrets)

### Example Bug Report

```
Title: DuckDB connection fails with special characters in password

Environment:
- Python 3.11
- Ubuntu 22.04
- metricforge 0.1.0

Steps:
1. Create metricforge.yaml with password containing '@' character
2. Run python -c "from metricforge.utils import MetricForgeConfig; MetricForgeConfig().get_data_warehouse_provider().validate_connection()"

Expected: Connection should succeed

Actual: ConnectionError: unable to parse connection string

Error:
```
duckdb.IOException: ...
```

Configuration:
```yaml
data_warehouse:
  type: duckdb_local
  config:
    database_path: ./db/test.duckdb
```
```

## Feature Requests

For feature ideas, open a GitHub Issue with:
- Description of desired functionality
- Use case/motivation
- Proposed implementation (optional)
- Examples from other tools (optional)

We'll discuss and prioritize in the issue.

## Questions and Discussions

- [GitHub Discussions](https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible/discussions) for questions
- [GitHub Issues](https://github.com/MetricForge-Analytics-Inc/MetricForge-Crucible/issues) for bugs and feature requests

## Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read and follow our Code of Conduct (to be added).

## License

By contributing, you agree that your contributions will be licensed under the same MIT license as the project.

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- GitHub contributors page
- Release notes

Thank you for making MetricForge better! 🎉

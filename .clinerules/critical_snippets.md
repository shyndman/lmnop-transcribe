## PROJECT SNIPPETS
### Activating the Virtual Environment
```sh
# ALWAYS RUN THIS WITHOUT &&s TO PERSIST CHANGES
. .venv/bin/activate
```

### Adding a Dependency
```sh
uv add {dependency} # Runtime required
uv add --dev {dependency} # Development
```

### Running the Binary
```sh
python -m lmnop_transcribe --config config.toml 2>&1 | tee application.log
```

### Running Tests
```sh
uv run pytest tests
```f

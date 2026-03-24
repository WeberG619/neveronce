# Changelog

All notable changes to NeverOnce will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-03-22

### Added
- `@guard` decorator for automatic correction enforcement
- Integration helpers for LangChain, CrewAI, and AutoGen
- MCP server with full tool support (`neveronce-mcp`)
- `search()` method with FTS5 full-text search
- `export_json()` and `import_json()` for data portability
- Cross-platform CI testing (Ubuntu, Windows, macOS × Python 3.10–3.13)
- 74 passing tests

### Changed
- Corrections now include context and timestamp metadata
- Improved `recall()` to always surface corrections first regardless of query

## [0.1.0] - 2026-03-18

### Added
- Initial release
- Core `Memory` class with SQLite backend
- `remember()`, `correct()`, `recall()` API
- Corrections-first retrieval — corrections never decay
- Zero dependencies (pure Python stdlib)
- `pip install neveronce` on PyPI

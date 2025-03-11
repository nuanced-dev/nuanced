# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.4] - 2025-03-11

### Added

### Fixed

### Changed

- Update `enrich` CLI command to search for graph in subdirectories as well as current working directory (https://github.com/nuanced-dev/nuanced/pull/54)
  - When one graph is found, the enrichment query is executed
  - When multiple graphs are found, an error is surfaced: `"Multiple Nuanced Graphs found in <dir>"`
  - When no graphs are found, an error is surfaced: `"Nuanced Graph not found in <dir>"`

### Removed

## [0.1.3] - 2025-03-05

### Added

### Fixed

- Update jarviscg dependency source for PyPI compatibility (https://github.com/nuanced-dev/nuanced/pull/46)
- Bump incorrect version number in `src/nuanced/__init__.py` (https://github.com/nuanced-dev/nuanced/pull/46)

### Changed

- Update minimum required Python version from 3.8 to 3.10 to reflect current behavior (https://github.com/nuanced-dev/nuanced/pull/46)

### Removed

- Disallow direct references for hatch (https://github.com/nuanced-dev/nuanced/pull/46)

## [0.1.2] - 2025-03-04

### Added

- MIT license

### Fixed

- Fix hatch configuration for jarviscg dependency (https://github.com/nuanced-dev/nuanced/pull/43)

### Changed

### Removed

## [0.1.1] - 2025-03-04

### Added

- nuanced Python library
  - Initializing graph using jarviscg
  - Enriching a function

- nuanced CLI

### Fixed

### Changed

### Removed

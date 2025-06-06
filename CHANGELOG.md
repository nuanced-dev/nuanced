# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.7] - 2025-06-05

### Added

- Introduce `nuanced --version` and `nuanced -v` CLI options for displaying installed version of nuanced (https://github.com/nuanced-dev/nuanced/pull/78)
- `CodeGraph::enrich` and `nuanced enrich` CLI command output includes edges to imported modules' attributes via jarviscg v0.1.0rc5 (https://github.com/nuanced-dev/nuanced/pull/76)

### Fixed

### Changed

- `CodeGraph::enrich` and `nuanced enrich` CLI command output excludes builtins from callees by default with the option to include them (https://github.com/nuanced-dev/nuanced/pull/77)
  - `CodeGraph::enrich` supports `include_builtins` keyword argument
  - `nuanced enrich` supports `--include-builtins` flag

### Removed

## [0.1.6] - 2025-05-27

### Added

### Fixed

### Changed

- Pretty-print `nuanced enrich` CLI command JSON output (https://github.com/nuanced-dev/nuanced/pull/71)
- Print CLI error messages to STDERR instead of STDOUT (https://github.com/nuanced-dev/nuanced/pull/73)
- Increase graph initialization timeout threshold from 30s to 60s (https://github.com/nuanced-dev/nuanced/pull/74)

### Removed

## [0.1.5] - 2025-05-05

### Added

### Fixed

### Changed

- Upgrade to jarviscg v0.1.0rc3 (https://github.com/nuanced-dev/nuanced/pull/63)
- Restrict usage to analyzing one package at a time by updating `CodeGraph.init` to ensure input path is a directory containing a package definition (https://github.com/nuanced-dev/nuanced/pull/66)
- Update `enrich` CLI command to search for and load the graph file that is relevant to the query (https://github.com/nuanced-dev/nuanced/pull/67)
  - Attempt to load a graph from the directory in which the file in `file_path` is located
  - If that doesn't work, traverse the directory structure starting with the top-level directory in `file_path` until graph is found

### Removed

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

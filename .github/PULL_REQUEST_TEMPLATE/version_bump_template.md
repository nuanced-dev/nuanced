Pre-review checklist:
- [ ] The version number in `pyproject.toml` has been updated
- [ ] `__version__` in `src/nuanced/__init__.py` has been updated
- [ ] `uv.lock` has been updated by running `uv sync`
- [ ] `CHANGELOG.md` has been updated

Post-merge checklist:
- [ ] Create GitHub Release
- [ ] Publish package to TestPyPI
- [ ] Publish package to PyPI
- [ ] Verify installation
  - [ ] `pip install nuanced`
  - [ ] `uv tool install nuanced`

References:
 - [nuanced Release Process](https://docs.nuanced.dev/versioning#release-process)

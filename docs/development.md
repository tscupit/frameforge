# FrameForge development setup

FrameForge is currently a fork of PurffleShorts. The Python distribution and
import module retain their upstream names (`purffle-shorts` and
`purffle_shorts`) until a separate compatibility-conscious rename.

## Requirements

- Python 3.10 or newer (Python 3.12 recommended)
- FFmpeg available on your PATH
- Git

The commands below run locally. Virtual environments, downloaded packages,
and credentials are not shared through Git.

## macOS

Install the prerequisites with Homebrew:

```bash
brew install python@3.12 ffmpeg
```

Clone the repository and set up an isolated environment:

```bash
git clone https://github.com/tscupit/frameforge.git
cd frameforge
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest -q
```

## Windows (PowerShell)

Install Python 3.12 and FFmpeg for Windows, ensuring FFmpeg is on PATH.
The Python launcher should recognize Python 3.12.

```powershell
git clone https://github.com/tscupit/frameforge.git
cd frameforge
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q
```

If PowerShell blocks activation, use the environment's interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
```

## Verification

```bash
python --version
ffmpeg -version
python -m ruff check .
python -m pytest -q
```

An initial local baseline was observed on macOS on 2026-10-26:
Python 3.12.16, FFmpeg 9.0.2, **232 passed, 2 skipped** in 129.60 seconds.
This is a local observation, not a claim that every CI platform has passed.

## Development workflow

1. Create a topic branch from `main`.
2. Make focused changes without committing credentials or generated assets.
3. Run lint and tests locally.
4. Open a pull request and inspect CI before merging.

The existing CLI remains `python -m purffle_shorts` and the installed
command remains `purffle-shorts` for now.

## Publishing safeguard

The `.github/workflows/release.yml` workflow validates build artifacts
without publishing to PyPI, GHCR, or the MCP Registry. Publishing must be
explicitly designed and configured for FrameForge before enabling it.

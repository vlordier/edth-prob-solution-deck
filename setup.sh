#!/usr/bin/env bash
set -euo pipefail

# EDTH Agent Setup — cross-platform (macOS, Linux, Windows/WSL)
# Detects platform, installs uv if missing, syncs deps, sets up pre-commit hooks.

BOLD="\033[1m"
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

info()  { echo -e "${GREEN}→${RESET} $*"; }
warn()  { echo -e "${YELLOW}→${RESET} $*"; }
error() { echo -e "${RED}→${RESET} $*"; }

# ── Detect platform ──
OS="$(uname -s)"
case "$OS" in
    Darwin)  PLATFORM="macOS"  ;;
    Linux)   PLATFORM="linux"  ;;
    MINGW*|MSYS*|CYGWIN*)   PLATFORM="windows"  ;;
    *)       PLATFORM="unknown" ;;
esac

info "Detected platform: $PLATFORM ($OS)"

# ── Check for Python 3.11+ ──
PYTHON=""
for cmd in python3.13 python3.12 python3.11 python3; do
    if command -v "$cmd" &>/dev/null; then
        ver=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
        major=$(echo "$ver" | cut -d. -f1)
        minor=$(echo "$ver" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 11 ]; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    error "Python 3.11+ not found. Install from https://python.org"
    info "macOS: brew install python@3.13"
    info "Linux: sudo apt install python3.13 (or your distro's package)"
    info "Windows: winget install Python.Python.3.13"
    exit 1
fi

info "Python: $($PYTHON --version)"

# ── Install uv if missing ──
if command -v uv &>/dev/null; then
    info "uv found: $(uv --version)"
else
    info "Installing uv..."
    if [ "$PLATFORM" = "windows" ]; then
        powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
        # PowerShell install puts uv in user path; WSL uses bash path
    else
        curl -LsSf https://astral.sh/uv/install.sh | sh
    fi
    # Ensure ~/.local/bin is on PATH (Linux/macOS default)
    export PATH="$HOME/.local/bin:$PATH"
    if command -v uv &>/dev/null; then
        info "uv installed successfully"
    else
        error "uv installation failed. Try: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
fi

# ── Sync Python deps ──
info "Syncing Python dependencies..."
uv sync --all-groups 2>&1 | tail -3

# ── Set up pre-commit hooks ──
if command -v pre-commit &>/dev/null; then
    info "Installing pre-commit hooks..."
    pre-commit install --install-hooks 2>&1 | tail -3
else
    warn "pre-commit not found. Install it to get automatic linting on commit:"
    info "  pip install pre-commit   # or: brew install pre-commit"
    info "  pre-commit install --install-hooks"
    warn "Skipping pre-commit setup for now."
fi

# ── Run tests ──
info "Running tests..."
uv run pytest -q

# ── Run linter ──
info "Running ruff linter..."
uv run ruff check agent/ tests/ 2>&1 || warn "Ruff found issues (review and fix if needed)"

echo ""
echo -e "${GREEN}${BOLD}✅ Setup complete!${RESET}"
echo ""
echo "  Next steps:"
echo "    cd $(pwd)"
echo "    opencode           # or: claude"
echo "    /edth-agent dry-run"
echo ""
echo "  If pre-commit is installed, ruff + markdownlint will run on every commit."

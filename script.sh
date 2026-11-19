
#!/usr/bin/env bash

set -uo pipefail

# ==========================================
# Django Project Auto Linter & Fixer
# ==========================================

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

ERRORS=0

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ERRORS=$((ERRORS + 1))
}

# ==========================================
# 1. Check dependencies
# ==========================================

info "Checking dependencies..."

if ! command -v python >/dev/null 2>&1; then
    error "Python not found"
    exit 1
fi

if ! python -c "import django" >/dev/null 2>&1; then
    error "Django is not installed"
    exit 1
fi

for tool in ruff mypy bandit; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        warning "$tool not installed"
    fi
done

# ==========================================
# 2. Ruff auto fix
# ==========================================

if command -v ruff >/dev/null 2>&1; then

    info "Fixing Python lint issues..."

    ruff check . --fix \
        --exclude migrations \
        --exclude .venv || error "Ruff autofix failed"

    info "Formatting Python code..."

    ruff format . \
        --exclude migrations \
        --exclude .venv || error "Formatting failed"

    success "Ruff completed"

else
    warning "Ruff skipped"
fi

# ==========================================
# 3. Django system checks
# ==========================================

info "Running Django checks..."

if [ -f manage.py ]; then

    python manage.py check || error "Django system check failed"

    python manage.py check --deploy || warning "Deployment checks reported issues"

else
    warning "manage.py not found"
fi

# ==========================================
# 4. Mypy type checking
# ==========================================

if command -v mypy >/dev/null 2>&1; then

    info "Checking Python types..."

    mypy . || error "Mypy found type errors"

else
    warning "Mypy skipped"
fi

# ==========================================
# 5. Bandit security check
# ==========================================

if command -v bandit >/dev/null 2>&1; then

    info "Checking security..."

    bandit -r . \
        -x ./.venv,./venv,./tests,./migrations \
        || error "Bandit found security issues"

else
    warning "Bandit skipped"
fi

# ==========================================
# 6. Run tests
# ==========================================

if python -c "import pytest" >/dev/null 2>&1; then

    info "Running tests..."

    pytest || error "Tests failed"

else
    warning "Pytest not installed, skipping tests"
fi

# ==========================================
# 7. Final report
# ==========================================

echo ""
echo "=========================================="

if [ "$ERRORS" -eq 0 ]; then
    success "All checks completed successfully!"
else
    error "Completed with $ERRORS failed checks"
fi

echo "=========================================="

echo "$ERRORS"

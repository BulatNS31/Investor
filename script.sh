#!/usr/bin/env bash

set -uo pipefail

# ==========================================
# Django Project Auto Linter & Fixer
# ==========================================
#
# Переменные окружения (необязательные):
#   DEV_SETTINGS   модуль dev-настроек   (по умолчанию config.settings.dev)
#   PROD_SETTINGS  модуль prod-настроек  (по умолчанию config.settings.prod)
#   PYTHON         интерпретатор Python  (по умолчанию python, затем python3)

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

DEV_SETTINGS="${DEV_SETTINGS:-config.settings.dev}"
PROD_SETTINGS="${PROD_SETTINGS:-config.settings.prod}"

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

if [ -z "${PYTHON:-}" ]; then
    if command -v python >/dev/null 2>&1; then
        PYTHON=python
    elif command -v python3 >/dev/null 2>&1; then
        PYTHON=python3
    else
        error "Python not found"
        exit 1
    fi
fi

if ! "$PYTHON" -c "import django" >/dev/null 2>&1; then
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

    # --extend-exclude добавляет исключения к стандартным, а не заменяет их
    ruff check . --fix \
        --extend-exclude migrations \
        --extend-exclude .venv || error "Ruff autofix failed (remaining issues need manual fixes)"

    info "Formatting Python code..."

    ruff format . \
        --extend-exclude migrations \
        --extend-exclude .venv || error "Formatting failed"

    success "Ruff completed"

else
    warning "Ruff skipped"
fi

# ==========================================
# 3. Django system checks
# ==========================================

if [ -f manage.py ]; then

    info "Running Django checks (dev settings: $DEV_SETTINGS)..."

    "$PYTHON" manage.py check --settings="$DEV_SETTINGS" \
        || error "Django system check failed"

    info "Running deployment checks (prod settings: $PROD_SETTINGS)..."

    # prod.py намеренно падает без секретов, поэтому для проверки подставляем
    # одноразовые значения. Экспортированные переменные имеют приоритет над .env
    # (load_dotenv не перезаписывает уже заданные), так что слабый ключ из .env
    # проверку не ломает. Реальные секреты в этот процесс не попадают.
    CHECK_SECRET_KEY="$("$PYTHON" -c \
        'from django.core.management.utils import get_random_secret_key as k; print(k())')"

    # --fail-level WARNING: без него предупреждения не меняют код возврата,
    # и проверка "проходила" бы даже с security.W***
    env \
        SECRET_KEY="$CHECK_SECRET_KEY" \
        ALLOWED_HOSTS="example.com" \
        DB_PASSWORD="deploy-check" \
        CORS_ALLOWED_ORIGINS="https://example.com" \
        CSRF_TRUSTED_ORIGINS="https://example.com" \
        "$PYTHON" manage.py check --deploy --fail-level WARNING --settings="$PROD_SETTINGS" \
        || error "Deployment checks reported issues"

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

    # Шаблоны с */ покрывают вложенные каталоги (apps/*/migrations, apps/*/tests)
    bandit -r . -q \
        -x './.venv,./venv,*/migrations,*/migrations/*,*/tests,*/tests/*' \
        || error "Bandit found security issues"

else
    warning "Bandit skipped"
fi

# ==========================================
# 6. Run tests
# ==========================================

if "$PYTHON" -c "import pytest" >/dev/null 2>&1; then

    info "Running tests..."

    DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-$DEV_SETTINGS}" \
        "$PYTHON" -m pytest
    PYTEST_RC=$?

    if [ "$PYTEST_RC" -eq 5 ]; then
        warning "No tests collected"
    elif [ "$PYTEST_RC" -ne 0 ]; then
        error "Tests failed"
    fi

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
    echo -e "${RED}[ERROR]${NC} Completed with $ERRORS failed checks"
fi

echo "=========================================="

if [ "$ERRORS" -ne 0 ]; then
    echo "Fix the issues above and run again."
    exit 1
fi
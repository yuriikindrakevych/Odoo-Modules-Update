#!/bin/bash

#######################################
# Odoo 18 Modules Analysis Script
# Аналіз кастомних модулів перед міграцією
# Автор: Claude Code
# Версія: 1.0
#######################################

set -e

# Кольори
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Конфігурація
ODOO_DIR="/www/wwwroot/odoo18-migration"
CUSTOM_ADDONS_DIR="${ODOO_DIR}/custom_addons"
ODOO_ADDONS_DIR="${ODOO_DIR}/odoo/addons"
CONFIG_FILE="${ODOO_DIR}/odoo18.conf"
LOG_DIR="${ODOO_DIR}/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="${LOG_DIR}/module_analysis_${TIMESTAMP}.log"
SUMMARY_FILE="${LOG_DIR}/module_summary_${TIMESTAMP}.md"

# PostgreSQL
DB_HOST="localhost"
DB_PORT="5433"
DB_USER="odoo"
DB_NAME="odoo18"
export PGPASSWORD="odoo"

#######################################
# Функції логування
#######################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    echo "[INFO] $1" >> "$REPORT_FILE"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
    echo "[OK] $1" >> "$REPORT_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    echo "[WARN] $1" >> "$REPORT_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "[ERROR] $1" >> "$REPORT_FILE"
}

log_detail() {
    echo -e "${CYAN}       $1${NC}"
    echo "       $1" >> "$REPORT_FILE"
}

#######################################
# Ініціалізація
#######################################

init() {
    mkdir -p "$LOG_DIR"
    echo "========================================" > "$REPORT_FILE"
    echo "Odoo 18 Module Analysis Report" >> "$REPORT_FILE"
    echo "Date: $(date)" >> "$REPORT_FILE"
    echo "========================================" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"

    # Markdown summary
    cat > "$SUMMARY_FILE" << 'EOF'
# Звіт аналізу модулів Odoo 18

## Легенда статусів

| Статус | Опис |
|--------|------|
| ✅ ACTIVE | Модуль активно використовується, є дані в БД |
| ⚠️ MINIMAL | Модуль встановлений, але мало даних |
| ❌ UNUSED | Модуль не використовується, можна не встановлювати |
| 🔄 REPLACEABLE | Є коробкова заміна в Odoo 18 |
| 🔗 REQUIRED | Потрібний як залежність для інших модулів |
| ⚡ STANDALONE | Незалежний модуль, можна встановити окремо |

---

EOF
}

#######################################
# Перевірка стану модуля в БД
#######################################

check_module_state() {
    local module=$1
    local state=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c \
        "SELECT state FROM ir_module_module WHERE name = '$module';" 2>/dev/null | tr -d ' ')
    echo "$state"
}

#######################################
# Підрахунок записів в таблицях модуля
#######################################

count_module_records() {
    local module=$1
    local total=0

    # Знайти моделі модуля
    local models=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c \
        "SELECT model FROM ir_model WHERE modules LIKE '%$module%';" 2>/dev/null | tr -d ' ')

    for model in $models; do
        # Конвертувати model.name в table_name
        local table=$(echo "$model" | tr '.' '_')
        local count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c \
            "SELECT COUNT(*) FROM $table;" 2>/dev/null | tr -d ' ')
        if [ -n "$count" ] && [ "$count" -gt 0 ]; then
            total=$((total + count))
        fi
    done 2>/dev/null

    echo "$total"
}

#######################################
# Перевірка залежностей модуля
#######################################

get_module_dependencies() {
    local module=$1
    local manifest="${CUSTOM_ADDONS_DIR}/${module}/__manifest__.py"

    if [ -f "$manifest" ]; then
        # Витягнути depends з manifest
        grep -oP "(?<='depends':\s*\[)[^\]]*" "$manifest" 2>/dev/null | \
            tr -d "'" | tr -d '"' | tr ',' '\n' | tr -d ' ' | grep -v '^$'
    fi
}

#######################################
# Перевірка хто залежить від модуля
#######################################

get_dependent_modules() {
    local module=$1
    local dependents=""

    for m in "$CUSTOM_ADDONS_DIR"/*/; do
        local mname=$(basename "$m")
        local manifest="${m}__manifest__.py"
        if [ -f "$manifest" ]; then
            if grep -q "'$module'" "$manifest" 2>/dev/null || grep -q "\"$module\"" "$manifest" 2>/dev/null; then
                dependents="$dependents $mname"
            fi
        fi
    done

    echo "$dependents" | tr -s ' ' | sed 's/^ //'
}

#######################################
# Перевірка коробкової заміни в Odoo 18
#######################################

check_odoo18_replacement() {
    local module=$1
    local replacement=""

    # Маппінг кастомних модулів на стандартні Odoo 18
    case "$module" in
        # Бухгалтерія та бюджети
        "base_account_budget")
            replacement="account_budget (Odoo Enterprise) або budget_management (Community)"
            ;;
        "account_dynamic_reports")
            replacement="Вбудовані звіти в Accounting модулі Odoo 18"
            ;;
        "base_accounting_kit")
            replacement="Часткова заміна вбудованими функціями Odoo 18 Accounting"
            ;;

        # CRM
        "crm_facebook_leads")
            replacement="crm_facebook (OCA) або Social Marketing (Enterprise)"
            ;;

        # API
        "openapi")
            replacement="Вбудований REST API в Odoo 17+ (часткова заміна)"
            ;;
        "base_api")
            replacement="Вбудований JSON-RPC API"
            ;;

        # Пошта
        "mail_debrand")
            replacement="Налаштування в System Parameters"
            ;;

        # Локалізація
        "l10n_ua")
            replacement="OCA/l10n-ukraine репозиторій для Odoo 18"
            ;;

        # Штрих-коди
        "barcodes_generator_abstract")
            replacement="Вбудований barcode модуль в Odoo 18"
            ;;

        # Взаєморозрахунки
        "account_netting")
            replacement="OCA/account-financial-tools для Odoo 18"
            ;;

        *)
            replacement=""
            ;;
    esac

    echo "$replacement"
}

#######################################
# Аналіз одного модуля
#######################################

analyze_module() {
    local module=$1
    local manifest="${CUSTOM_ADDONS_DIR}/${module}/__manifest__.py"

    echo "" >> "$REPORT_FILE"
    echo "----------------------------------------" >> "$REPORT_FILE"
    log_info "Аналіз модуля: $module"

    # Перевірка наявності модуля
    if [ ! -d "${CUSTOM_ADDONS_DIR}/${module}" ]; then
        log_error "Модуль не знайдено в ${CUSTOM_ADDONS_DIR}"
        return
    fi

    # Версія модуля
    local version=$(grep -oP "(?<=['\"]version['\"]:\s*['\"])[^'\"]*" "$manifest" 2>/dev/null | head -1)
    log_detail "Версія: $version"

    # Стан в БД
    local state=$(check_module_state "$module")
    log_detail "Стан в БД: ${state:-не встановлений}"

    # Кількість записів
    local records=$(count_module_records "$module")
    log_detail "Записів в БД: $records"

    # Залежності
    local deps=$(get_module_dependencies "$module")
    if [ -n "$deps" ]; then
        log_detail "Залежить від: $(echo $deps | tr '\n' ', ' | sed 's/,$//')"
    fi

    # Хто залежить від цього модуля
    local dependents=$(get_dependent_modules "$module")
    if [ -n "$dependents" ]; then
        log_detail "Від нього залежать: $dependents"
    fi

    # Коробкова заміна
    local replacement=$(check_odoo18_replacement "$module")
    if [ -n "$replacement" ]; then
        log_warning "Можлива заміна: $replacement"
    fi

    # Визначення статусу
    local status=""
    local recommendation=""

    if [ -n "$replacement" ]; then
        status="🔄 REPLACEABLE"
        recommendation="Розглянути коробкову заміну: $replacement"
    elif [ -n "$dependents" ]; then
        status="🔗 REQUIRED"
        recommendation="Потрібен для: $dependents"
    elif [ "$state" = "installed" ] && [ "$records" -gt 100 ]; then
        status="✅ ACTIVE"
        recommendation="Активно використовується, обов'язково встановити"
    elif [ "$state" = "installed" ] && [ "$records" -gt 0 ]; then
        status="⚠️ MINIMAL"
        recommendation="Мало даних, перевірити необхідність"
    elif [ "$state" = "installed" ]; then
        status="❌ UNUSED"
        recommendation="Немає даних, можна не встановлювати"
    else
        status="⚡ STANDALONE"
        recommendation="Незалежний модуль, встановити за потреби"
    fi

    log_success "Статус: $status"
    log_detail "Рекомендація: $recommendation"

    # Додати до summary
    echo "| \`$module\` | $version | $status | ${records:-0} | $recommendation |" >> "$SUMMARY_FILE"
}

#######################################
# Перевірка моделей з помилками
#######################################

check_broken_models() {
    log_info "Перевірка моделей з помилками..."

    local broken=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c \
        "SELECT model FROM ir_model WHERE transient = false AND model NOT IN (
            SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'
        );" 2>/dev/null)

    if [ -n "$broken" ]; then
        log_warning "Знайдено моделі без таблиць:"
        echo "$broken" | while read model; do
            [ -n "$model" ] && log_detail "- $model"
        done
    else
        log_success "Всі моделі мають таблиці в БД"
    fi
}

#######################################
# Перевірка views з помилками
#######################################

check_broken_views() {
    log_info "Перевірка views з помилками..."

    local broken_views=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c \
        "SELECT name FROM ir_ui_view WHERE active = true AND arch_db IS NULL;" 2>/dev/null)

    if [ -n "$broken_views" ]; then
        log_warning "Знайдено views без arch:"
        echo "$broken_views" | while read view; do
            [ -n "$view" ] && log_detail "- $view"
        done
    else
        log_success "Всі активні views мають arch"
    fi
}

#######################################
# Перевірка залежностей всіх модулів
#######################################

check_all_dependencies() {
    log_info "Аналіз графу залежностей..."

    echo "" >> "$SUMMARY_FILE"
    echo "## Граф залежностей" >> "$SUMMARY_FILE"
    echo "" >> "$SUMMARY_FILE"
    echo '```' >> "$SUMMARY_FILE"

    for module_dir in "$CUSTOM_ADDONS_DIR"/*/; do
        local module=$(basename "$module_dir")
        [ "$module" = "docs" ] && continue

        local deps=$(get_module_dependencies "$module")
        local custom_deps=""

        for dep in $deps; do
            if [ -d "${CUSTOM_ADDONS_DIR}/${dep}" ]; then
                custom_deps="$custom_deps $dep"
            fi
        done

        if [ -n "$custom_deps" ]; then
            echo "$module -> $custom_deps" >> "$SUMMARY_FILE"
        fi
    done

    echo '```' >> "$SUMMARY_FILE"
}

#######################################
# Генерація рекомендацій
#######################################

generate_recommendations() {
    echo "" >> "$SUMMARY_FILE"
    echo "## Рекомендації по встановленню" >> "$SUMMARY_FILE"
    echo "" >> "$SUMMARY_FILE"

    echo "### 1. Обов'язкові модулі (ACTIVE + REQUIRED)" >> "$SUMMARY_FILE"
    echo "Ці модулі активно використовуються або потрібні як залежності:" >> "$SUMMARY_FILE"
    echo "" >> "$SUMMARY_FILE"

    echo "### 2. Модулі для перевірки (MINIMAL)" >> "$SUMMARY_FILE"
    echo "Перевірити чи потрібні ці модулі:" >> "$SUMMARY_FILE"
    echo "" >> "$SUMMARY_FILE"

    echo "### 3. Можна не встановлювати (UNUSED)" >> "$SUMMARY_FILE"
    echo "Ці модулі не мають даних в БД:" >> "$SUMMARY_FILE"
    echo "" >> "$SUMMARY_FILE"

    echo "### 4. Розглянути заміну (REPLACEABLE)" >> "$SUMMARY_FILE"
    echo "Для цих модулів є коробкові альтернативи в Odoo 18:" >> "$SUMMARY_FILE"
    echo "" >> "$SUMMARY_FILE"
}

#######################################
# Головна функція
#######################################

main() {
    echo ""
    echo "=========================================="
    echo "  Odoo 18 Module Analysis Tool"
    echo "=========================================="
    echo ""

    # Ініціалізація
    init

    # Перевірка підключення до БД
    log_info "Перевірка підключення до PostgreSQL..."
    if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
        log_error "Не вдалося підключитися до БД"
        exit 1
    fi
    log_success "Підключення до БД успішне"

    # Перевірка директорії модулів
    if [ ! -d "$CUSTOM_ADDONS_DIR" ]; then
        log_error "Директорія модулів не знайдена: $CUSTOM_ADDONS_DIR"
        exit 1
    fi

    # Заголовок таблиці в summary
    echo "## Результати аналізу модулів" >> "$SUMMARY_FILE"
    echo "" >> "$SUMMARY_FILE"
    echo "| Модуль | Версія | Статус | Записів | Рекомендація |" >> "$SUMMARY_FILE"
    echo "|--------|--------|--------|---------|--------------|" >> "$SUMMARY_FILE"

    # Аналіз кожного модуля
    local count=0
    for module_dir in "$CUSTOM_ADDONS_DIR"/*/; do
        local module=$(basename "$module_dir")

        # Пропустити не-модулі
        [ "$module" = "docs" ] && continue
        [ ! -f "${module_dir}__manifest__.py" ] && continue

        analyze_module "$module"
        count=$((count + 1))
    done

    echo "" >> "$REPORT_FILE"
    echo "========================================" >> "$REPORT_FILE"

    # Додаткові перевірки
    echo "" >> "$SUMMARY_FILE"
    check_broken_models
    check_broken_views
    check_all_dependencies
    generate_recommendations

    # Підсумок
    echo ""
    echo "=========================================="
    log_success "Аналіз завершено!"
    log_info "Проаналізовано модулів: $count"
    log_info "Детальний звіт: $REPORT_FILE"
    log_info "Summary (Markdown): $SUMMARY_FILE"
    echo "=========================================="
    echo ""
}

# Запуск
main "$@"

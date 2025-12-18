#!/bin/bash

#######################################
# Local Code Analysis Script
# Аналіз коду модулів без підключення до БД
# Можна запускати локально
#######################################

# Кольори
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Визначення директорії скрипта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="${PROJECT_DIR}/analysis_report_${TIMESTAMP}.md"

#######################################
# Коробкові заміни в Odoo 18
#######################################

declare -A ODOO18_REPLACEMENTS=(
    ["base_account_budget"]="account_budget (Enterprise) - Бюджети тепер в Enterprise версії"
    ["account_dynamic_reports"]="Вбудовані динамічні звіти в Accounting (часткова заміна)"
    ["base_accounting_kit"]="Багато функцій вже в стандартному Accounting модулі Odoo 18"
    ["crm_facebook_leads"]="Social Marketing (Enterprise) або OCA/crm-addons"
    ["openapi"]="Odoo 17+ має вбудований REST API (часткова заміна)"
    ["base_api"]="Вбудований JSON-RPC та новий REST API в Odoo 17+"
    ["mail_debrand"]="System Parameters: mail.catchall.domain, web.base.url"
    ["barcodes_generator_abstract"]="Вбудований barcode модуль покращений в Odoo 18"
    ["account_netting"]="OCA/account-financial-tools має версію для Odoo 18"
    ["l10n_ua"]="OCA/l10n-ukraine - перевірити наявність для v18"
)

#######################################
# Функції
#######################################

log_header() {
    echo -e "\n${BOLD}${BLUE}=== $1 ===${NC}\n"
    echo -e "\n## $1\n" >> "$REPORT_FILE"
}

log_module() {
    echo -e "${CYAN}📦 $1${NC}"
    echo -e "\n### $1\n" >> "$REPORT_FILE"
}

log_info() {
    echo -e "   ${GREEN}✓${NC} $1"
    echo "- $1" >> "$REPORT_FILE"
}

log_warn() {
    echo -e "   ${YELLOW}⚠${NC} $1"
    echo "- ⚠️ $1" >> "$REPORT_FILE"
}

log_error() {
    echo -e "   ${RED}✗${NC} $1"
    echo "- ❌ $1" >> "$REPORT_FILE"
}

#######################################
# Аналіз manifest файлу
#######################################

analyze_manifest() {
    local module_dir=$1
    local manifest="${module_dir}/__manifest__.py"

    if [ ! -f "$manifest" ]; then
        return 1
    fi

    # Версія
    local version=$(grep -oP "(?<=['\"]version['\"]:\s*['\"])[^'\"]*" "$manifest" | head -1)
    echo "   Версія: $version"
    echo "- Версія: \`$version\`" >> "$REPORT_FILE"

    # Залежності
    local depends=$(grep -oP "(?<=['\"]depends['\"]:\s*\[)[^\]]*" "$manifest" | tr -d "'" | tr -d '"' | tr ',' '\n' | tr -d ' ' | grep -v '^$')
    if [ -n "$depends" ]; then
        echo "   Залежності: $(echo $depends | tr '\n' ', ' | sed 's/,$//')"
        echo "- Залежності: \`$(echo $depends | tr '\n' ', ' | sed 's/,$//')\`" >> "$REPORT_FILE"
    fi

    # Автор
    local author=$(grep -oP "(?<=['\"]author['\"]:\s*['\"])[^'\"]*" "$manifest" | head -1)
    [ -n "$author" ] && echo "   Автор: $author"

    return 0
}

#######################################
# Аналіз Python коду
#######################################

analyze_python() {
    local module_dir=$1
    local issues=0

    # Кількість Python файлів
    local py_count=$(find "$module_dir" -name "*.py" | wc -l)
    echo "   Python файлів: $py_count"

    # Кількість рядків коду
    local loc=$(find "$module_dir" -name "*.py" -exec cat {} \; 2>/dev/null | wc -l)
    echo "   Рядків коду: $loc"
    echo "- Python: $py_count файлів, $loc рядків" >> "$REPORT_FILE"

    # Моделі
    local models=$(grep -rh "class.*models\." "$module_dir" --include="*.py" 2>/dev/null | wc -l)
    [ "$models" -gt 0 ] && echo "   Моделі ORM: $models"

    # Controllers (HTTP endpoints)
    local controllers=$(grep -rh "@http.route" "$module_dir" --include="*.py" 2>/dev/null | wc -l)
    if [ "$controllers" -gt 0 ]; then
        echo "   HTTP endpoints: $controllers"
        echo "- HTTP endpoints: $controllers" >> "$REPORT_FILE"
    fi

    # Wizards
    local wizards=$(grep -rh "TransientModel" "$module_dir" --include="*.py" 2>/dev/null | wc -l)
    [ "$wizards" -gt 0 ] && echo "   Wizards: $wizards"

    # Cron jobs
    local crons=$(grep -rl "ir.cron" "$module_dir" --include="*.xml" 2>/dev/null | wc -l)
    if [ "$crons" -gt 0 ]; then
        echo "   Cron jobs: $crons"
        echo "- Cron jobs: так" >> "$REPORT_FILE"
    fi

    return $issues
}

#######################################
# Аналіз XML views
#######################################

analyze_xml() {
    local module_dir=$1

    local xml_count=$(find "$module_dir" -name "*.xml" | wc -l)
    echo "   XML файлів: $xml_count"

    # Views
    local views=$(grep -rh "<record.*ir.ui.view" "$module_dir" --include="*.xml" 2>/dev/null | wc -l)
    [ "$views" -gt 0 ] && echo "   Views: $views"

    # Actions
    local actions=$(grep -rh "ir.actions" "$module_dir" --include="*.xml" 2>/dev/null | wc -l)
    [ "$actions" -gt 0 ] && echo "   Actions: $actions"

    # Security rules
    local rules=$(grep -rh "ir.rule" "$module_dir" --include="*.xml" 2>/dev/null | wc -l)
    [ "$rules" -gt 0 ] && echo "   Security rules: $rules"

    # Menu items
    local menus=$(grep -rh "<menuitem" "$module_dir" --include="*.xml" 2>/dev/null | wc -l)
    [ "$menus" -gt 0 ] && echo "   Menu items: $menus"

    echo "- XML: $xml_count файлів, $views views, $menus меню" >> "$REPORT_FILE"
}

#######################################
# Аналіз JavaScript
#######################################

analyze_js() {
    local module_dir=$1

    local js_count=$(find "$module_dir" -name "*.js" 2>/dev/null | wc -l)
    if [ "$js_count" -gt 0 ]; then
        echo "   JavaScript файлів: $js_count"
        echo "- JavaScript: $js_count файлів" >> "$REPORT_FILE"

        # OWL компоненти
        local owl=$(grep -rh "@odoo-module\|owl" "$module_dir" --include="*.js" 2>/dev/null | wc -l)
        [ "$owl" -gt 0 ] && echo "   OWL/ES6 модулі: присутні"

        # Legacy JS
        local legacy=$(grep -rh "odoo.define" "$module_dir" --include="*.js" 2>/dev/null | wc -l)
        if [ "$legacy" -gt 0 ]; then
            log_warn "Legacy JS (odoo.define): $legacy - потребує оновлення для Odoo 17+"
        fi
    fi
}

#######################################
# Аналіз data файлів
#######################################

analyze_data() {
    local module_dir=$1

    # Demo data
    local demo=$(find "$module_dir" -path "*/demo/*" -name "*.xml" 2>/dev/null | wc -l)
    [ "$demo" -gt 0 ] && echo "   Demo data файлів: $demo"

    # Data files
    local data=$(find "$module_dir" -path "*/data/*" -name "*.xml" 2>/dev/null | wc -l)
    [ "$data" -gt 0 ] && echo "   Data файлів: $data"

    # Translations
    local i18n=$(find "$module_dir" -path "*/i18n/*" -name "*.po" 2>/dev/null | wc -l)
    [ "$i18n" -gt 0 ] && echo "   Переклади: $i18n мов"

    # Security
    local security=$(find "$module_dir" -name "ir.model.access.csv" 2>/dev/null | wc -l)
    [ "$security" -gt 0 ] && echo "   Security CSV: присутній"
}

#######################################
# Перевірка коробкової заміни
#######################################

check_replacement() {
    local module=$1

    if [ -n "${ODOO18_REPLACEMENTS[$module]}" ]; then
        log_warn "Коробкова заміна: ${ODOO18_REPLACEMENTS[$module]}"
        return 0
    fi
    return 1
}

#######################################
# Визначення критичності модуля
#######################################

determine_importance() {
    local module_dir=$1
    local module=$(basename "$module_dir")
    local importance="MEDIUM"
    local reasons=""

    # Фактори важливості
    local has_models=$(grep -rh "class.*models\." "$module_dir" --include="*.py" 2>/dev/null | wc -l)
    local has_data=$(find "$module_dir" -path "*/data/*" -name "*.xml" 2>/dev/null | wc -l)
    local has_views=$(grep -rh "<record.*ir.ui.view" "$module_dir" --include="*.xml" 2>/dev/null | wc -l)
    local has_controllers=$(grep -rh "@http.route" "$module_dir" --include="*.py" 2>/dev/null | wc -l)
    local loc=$(find "$module_dir" -name "*.py" -exec cat {} \; 2>/dev/null | wc -l)

    # Високий пріоритет
    if [ "$has_models" -gt 5 ] || [ "$loc" -gt 1000 ] || [ "$has_controllers" -gt 3 ]; then
        importance="HIGH"
        reasons="Багато моделей/коду/API"
    fi

    # Низький пріоритет
    if [ "$has_models" -eq 0 ] && [ "$has_views" -lt 3 ] && [ "$loc" -lt 100 ]; then
        importance="LOW"
        reasons="Мінімальна функціональність"
    fi

    # Переклади
    if [[ "$module" == *"translate"* ]]; then
        importance="LOW"
        reasons="Тільки переклади"
    fi

    echo "   Важливість: $importance ${reasons:+($reasons)}"
    echo "- **Важливість: $importance** ${reasons:+- $reasons}" >> "$REPORT_FILE"
}

#######################################
# Аналіз залежностей між модулями
#######################################

analyze_dependencies_graph() {
    log_header "Граф залежностей кастомних модулів"

    echo '```mermaid' >> "$REPORT_FILE"
    echo 'graph TD' >> "$REPORT_FILE"

    for module_dir in "$PROJECT_DIR"/*/; do
        local module=$(basename "$module_dir")
        [ ! -f "${module_dir}__manifest__.py" ] && continue
        [ "$module" = "docs" ] || [ "$module" = "scripts" ] && continue

        local depends=$(grep -oP "(?<=['\"]depends['\"]:\s*\[)[^\]]*" "${module_dir}__manifest__.py" 2>/dev/null | tr -d "'" | tr -d '"' | tr ',' '\n' | tr -d ' ')

        for dep in $depends; do
            # Тільки кастомні залежності
            if [ -d "${PROJECT_DIR}/${dep}" ]; then
                echo "    ${module} --> ${dep}" >> "$REPORT_FILE"
            fi
        done
    done

    echo '```' >> "$REPORT_FILE"
}

#######################################
# Рекомендації по встановленню
#######################################

generate_install_order() {
    log_header "Рекомендований порядок встановлення"

    echo "На основі аналізу залежностей:" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "1. **Базові модулі** (без залежностей на інші кастомні):" >> "$REPORT_FILE"

    for module_dir in "$PROJECT_DIR"/*/; do
        local module=$(basename "$module_dir")
        [ ! -f "${module_dir}__manifest__.py" ] && continue
        [ "$module" = "docs" ] || [ "$module" = "scripts" ] && continue

        local custom_deps=0
        local depends=$(grep -oP "(?<=['\"]depends['\"]:\s*\[)[^\]]*" "${module_dir}__manifest__.py" 2>/dev/null | tr -d "'" | tr -d '"' | tr ',' '\n' | tr -d ' ')

        for dep in $depends; do
            [ -d "${PROJECT_DIR}/${dep}" ] && custom_deps=$((custom_deps + 1))
        done

        if [ "$custom_deps" -eq 0 ]; then
            echo "   - \`$module\`" >> "$REPORT_FILE"
        fi
    done

    echo "" >> "$REPORT_FILE"
    echo "2. **Залежні модулі** (встановлювати після базових)" >> "$REPORT_FILE"
}

#######################################
# Головна функція
#######################################

main() {
    echo -e "${BOLD}"
    echo "╔════════════════════════════════════════╗"
    echo "║   Odoo Modules Local Analysis Tool     ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"

    # Ініціалізація звіту
    cat > "$REPORT_FILE" << EOF
# Звіт аналізу модулів Odoo

**Дата:** $(date)
**Директорія:** $PROJECT_DIR

---

EOF

    log_header "Аналіз модулів"

    local total=0
    local with_replacement=0
    local high_priority=0

    for module_dir in "$PROJECT_DIR"/*/; do
        local module=$(basename "$module_dir")

        # Пропустити службові директорії
        [ ! -f "${module_dir}__manifest__.py" ] && continue
        [ "$module" = "docs" ] || [ "$module" = "scripts" ] && continue

        log_module "$module"

        analyze_manifest "$module_dir"
        analyze_python "$module_dir"
        analyze_xml "$module_dir"
        analyze_js "$module_dir"
        analyze_data "$module_dir"
        check_replacement "$module" && with_replacement=$((with_replacement + 1))
        determine_importance "$module_dir"

        total=$((total + 1))
        echo ""
    done

    # Граф залежностей
    analyze_dependencies_graph

    # Порядок встановлення
    generate_install_order

    # Підсумок
    log_header "Підсумок"

    echo "- Всього модулів: $total" >> "$REPORT_FILE"
    echo "- Модулів з коробковою заміною: $with_replacement" >> "$REPORT_FILE"

    echo -e "\n${BOLD}${GREEN}Аналіз завершено!${NC}"
    echo -e "Звіт збережено: ${CYAN}$REPORT_FILE${NC}\n"
}

# Запуск
main "$@"

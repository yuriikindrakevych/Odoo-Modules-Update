#!/bin/bash

#######################################
# Odoo 18 Custom Modules Deploy Script
# Автор: echo digital
# Версія: 2.0
# Сервер: odoo-18.aclima.ua
#######################################

set -e  # Зупинка при помилці

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Конфігурація
ODOO_DIR="/www/wwwroot/odoo-18.aclima.ua"
CUSTOM_ADDONS_DIR="${ODOO_DIR}/custom_addons"
VENV_DIR="${ODOO_DIR}/venv"
CONFIG_FILE="${ODOO_DIR}/odoo18.conf"
SERVICE_NAME="odoo18"
BACKUP_DIR="${ODOO_DIR}/backups"
LOG_DIR="${ODOO_DIR}/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
GIT_BRANCH="main"

# PostgreSQL конфігурація
DB_HOST="localhost"
DB_PORT="5432"
DB_USER="odoo"
DB_NAME="odoo18_new"

#######################################
# Функції
#######################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_sudo() {
    if [ "$EUID" -ne 0 ]; then
        log_error "Цей скрипт потрібно запускати через sudo"
        log_info "Використання: sudo $0 [КОМАНДА]"
        exit 1
    fi
}

show_help() {
    echo "Використання: sudo $0 [КОМАНДА] [ОПЦІЇ]"
    echo ""
    echo "Команди:"
    echo "  pull              Завантажити останні зміни з git"
    echo "  update [module]   Оновити модуль(і) в Odoo"
    echo "  update-all        Оновити всі кастомні модулі"
    echo "  install [module]  Встановити новий модуль"
    echo "  restart           Перезапустити Odoo сервіс"
    echo "  status            Показати статус сервісу"
    echo "  logs              Показати логи Odoo"
    echo "  backup            Створити бекап бази даних"
    echo "  restore [file]    Відновити базу з бекапу"
    echo "  test [module]     Тестувати модуль без перезапуску"
    echo "  deploy            Повний деплой (pull + update-all + restart)"
    echo "  help              Показати цю довідку"
    echo ""
    echo "Приклади:"
    echo "  sudo $0 pull"
    echo "  sudo $0 update mobius_lead_condition"
    echo "  sudo $0 update-all"
    echo "  sudo $0 deploy"
    echo ""
    echo "Конфігурація:"
    echo "  Odoo директорія: $ODOO_DIR"
    echo "  База даних: $DB_NAME"
    echo "  PostgreSQL порт: $DB_PORT"
    echo "  Сервіс: $SERVICE_NAME"
}

check_directories() {
    log_info "Перевірка директорій..."

    if [ ! -d "$ODOO_DIR" ]; then
        log_error "Директорія Odoo не знайдена: $ODOO_DIR"
        exit 1
    fi

    if [ ! -d "$CUSTOM_ADDONS_DIR" ]; then
        log_warning "Директорія кастомних модулів не знайдена, створюємо..."
        mkdir -p "$CUSTOM_ADDONS_DIR"
    fi

    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
    fi

    if [ ! -d "$LOG_DIR" ]; then
        mkdir -p "$LOG_DIR"
    fi

    log_success "Директорії перевірено"
}

git_pull() {
    log_info "Завантаження останніх змін з git..."
    cd "$CUSTOM_ADDONS_DIR"

    if [ ! -d ".git" ]; then
        log_error "Git репозиторій не ініціалізовано в $CUSTOM_ADDONS_DIR"
        exit 1
    fi

    # Зберегти поточну гілку
    CURRENT_BRANCH=$(git branch --show-current)

    # Перевірити наявність незбережених змін
    if [ -n "$(git status --porcelain)" ]; then
        log_warning "Є незбережені зміни. Зберігаємо в stash..."
        git stash
    fi

    # Переключитися на потрібну гілку якщо потрібно
    if [ "$CURRENT_BRANCH" != "$GIT_BRANCH" ]; then
        log_info "Переключення на гілку $GIT_BRANCH..."
        git checkout "$GIT_BRANCH"
    fi

    # Завантажити зміни
    git pull origin "$GIT_BRANCH"

    log_success "Git pull завершено"
}

update_module() {
    local module=$1

    if [ -z "$module" ]; then
        log_error "Не вказано назву модуля"
        exit 1
    fi

    log_info "Оновлення модуля: $module"

    cd "$ODOO_DIR"
    source "${VENV_DIR}/bin/activate"

    python odoo/odoo-bin -c "$CONFIG_FILE" \
        -u "$module" \
        --stop-after-init \
        --log-level=info 2>&1 | tee "${LOG_DIR}/update_${module}_${TIMESTAMP}.log"

    # Перевірка на помилки
    if grep -qi "error" "${LOG_DIR}/update_${module}_${TIMESTAMP}.log"; then
        log_warning "Виявлено помилки в логах. Перевірте: ${LOG_DIR}/update_${module}_${TIMESTAMP}.log"
    else
        log_success "Модуль $module оновлено успішно"
    fi

    deactivate
}

update_all_modules() {
    log_info "Оновлення всіх кастомних модулів..."

    # Отримати список всіх модулів
    local modules=""
    for dir in "$CUSTOM_ADDONS_DIR"/*/; do
        if [ -f "${dir}__manifest__.py" ]; then
            module_name=$(basename "$dir")
            if [ -z "$modules" ]; then
                modules="$module_name"
            else
                modules="${modules},${module_name}"
            fi
        fi
    done

    if [ -z "$modules" ]; then
        log_warning "Не знайдено кастомних модулів"
        return
    fi

    log_info "Модулі для оновлення: $modules"

    cd "$ODOO_DIR"
    source "${VENV_DIR}/bin/activate"

    python odoo/odoo-bin -c "$CONFIG_FILE" \
        -u "$modules" \
        --stop-after-init \
        --log-level=info 2>&1 | tee "${LOG_DIR}/update_all_${TIMESTAMP}.log"

    deactivate

    log_success "Всі модулі оновлено"
}

install_module() {
    local module=$1

    if [ -z "$module" ]; then
        log_error "Не вказано назву модуля"
        exit 1
    fi

    log_info "Встановлення модуля: $module"

    cd "$ODOO_DIR"
    source "${VENV_DIR}/bin/activate"

    python odoo/odoo-bin -c "$CONFIG_FILE" \
        -i "$module" \
        --stop-after-init \
        --log-level=info 2>&1 | tee "${LOG_DIR}/install_${module}_${TIMESTAMP}.log"

    deactivate

    log_success "Модуль $module встановлено"
}

restart_service() {
    log_info "Перезапуск Odoo сервісу..."

    systemctl restart "$SERVICE_NAME"
    sleep 3

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_success "Odoo сервіс перезапущено успішно"
    else
        log_error "Помилка перезапуску сервісу"
        systemctl status "$SERVICE_NAME"
        exit 1
    fi
}

stop_service() {
    log_info "Зупинка Odoo сервісу..."
    systemctl stop "$SERVICE_NAME"
    log_success "Odoo сервіс зупинено"
}

start_service() {
    log_info "Запуск Odoo сервісу..."
    systemctl start "$SERVICE_NAME"
    sleep 3

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_success "Odoo сервіс запущено успішно"
    else
        log_error "Помилка запуску сервісу"
        systemctl status "$SERVICE_NAME"
        exit 1
    fi
}

show_status() {
    log_info "Статус Odoo сервісу:"
    systemctl status "$SERVICE_NAME" --no-pager
}

show_logs() {
    log_info "Останні логи Odoo:"
    journalctl -u "$SERVICE_NAME" -f
}

create_backup() {
    log_info "Створення бекапу бази даних..."

    local backup_file="${BACKUP_DIR}/${DB_NAME}_backup_${TIMESTAMP}.sql"

    PGPASSWORD="$DB_USER" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" > "$backup_file"

    # Стиснення
    gzip "$backup_file"

    log_success "Бекап створено: ${backup_file}.gz"

    # Видалення старих бекапів (залишити останні 5)
    cd "$BACKUP_DIR"
    ls -t *.sql.gz 2>/dev/null | tail -n +6 | xargs -r rm

    log_info "Старі бекапи очищено"
}

restore_backup() {
    local backup_file=$1

    if [ -z "$backup_file" ]; then
        log_error "Не вказано файл бекапу"
        echo "Доступні бекапи:"
        ls -la "$BACKUP_DIR"/*.sql.gz 2>/dev/null || echo "Бекапи не знайдено"
        exit 1
    fi

    if [ ! -f "$backup_file" ]; then
        # Перевірити в директорії бекапів
        if [ -f "${BACKUP_DIR}/${backup_file}" ]; then
            backup_file="${BACKUP_DIR}/${backup_file}"
        else
            log_error "Файл бекапу не знайдено: $backup_file"
            exit 1
        fi
    fi

    log_warning "УВАГА! Це видалить поточну базу даних!"
    read -p "Продовжити? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        log_info "Відновлення скасовано"
        exit 0
    fi

    log_info "Зупинка Odoo сервісу..."
    systemctl stop "$SERVICE_NAME"

    log_info "Відновлення бази даних..."

    # Розпакувати якщо .gz
    if [[ "$backup_file" == *.gz ]]; then
        gunzip -k "$backup_file"
        backup_file="${backup_file%.gz}"
    fi

    # Видалити та створити базу заново
    PGPASSWORD="$DB_USER" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres \
        -c "DROP DATABASE IF EXISTS $DB_NAME;"
    PGPASSWORD="$DB_USER" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres \
        -c "CREATE DATABASE $DB_NAME;"

    # Відновити
    PGPASSWORD="$DB_USER" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        < "$backup_file"

    log_info "Запуск Odoo сервісу..."
    systemctl start "$SERVICE_NAME"

    log_success "База даних відновлена з $backup_file"
}

test_module() {
    local module=$1

    if [ -z "$module" ]; then
        log_error "Не вказано назву модуля"
        exit 1
    fi

    log_info "Тестування модуля: $module (без перезапуску сервісу)"

    cd "$ODOO_DIR"
    source "${VENV_DIR}/bin/activate"

    python odoo/odoo-bin -c "$CONFIG_FILE" \
        -u "$module" \
        --stop-after-init \
        --test-enable \
        --log-level=test 2>&1 | tee "${LOG_DIR}/test_${module}_${TIMESTAMP}.log"

    deactivate

    log_success "Тестування завершено. Лог: ${LOG_DIR}/test_${module}_${TIMESTAMP}.log"
}

full_deploy() {
    log_info "=== Повний деплой ==="

    # Створити бекап перед деплоєм
    create_backup

    # Завантажити зміни
    git_pull

    # Зупинити сервіс
    log_info "Зупинка Odoo сервісу..."
    systemctl stop "$SERVICE_NAME"

    # Оновити всі модулі
    update_all_modules

    # Запустити сервіс
    log_info "Запуск Odoo сервісу..."
    systemctl start "$SERVICE_NAME"
    sleep 5

    # Перевірити статус
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_success "=== Деплой завершено успішно ==="
    else
        log_error "Помилка запуску сервісу після деплою"
        systemctl status "$SERVICE_NAME"
        exit 1
    fi
}

#######################################
# Головна логіка
#######################################

# Перевірка sudo (крім help)
if [ "${1:-help}" != "help" ] && [ "${1:-help}" != "--help" ] && [ "${1:-help}" != "-h" ]; then
    check_sudo
fi

# Перевірка директорій (крім help)
if [ "${1:-help}" != "help" ] && [ "${1:-help}" != "--help" ] && [ "${1:-help}" != "-h" ]; then
    check_directories
fi

# Обробка команд
case "${1:-help}" in
    pull)
        git_pull
        ;;
    update)
        update_module "$2"
        ;;
    update-all)
        update_all_modules
        ;;
    install)
        install_module "$2"
        ;;
    restart)
        restart_service
        ;;
    stop)
        stop_service
        ;;
    start)
        start_service
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    backup)
        create_backup
        ;;
    restore)
        restore_backup "$2"
        ;;
    test)
        test_module "$2"
        ;;
    deploy)
        full_deploy
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Невідома команда: $1"
        show_help
        exit 1
        ;;
esac

exit 0

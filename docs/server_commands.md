# Команди для деплою на сервер

## 📋 Підготовка сервера

### 1. Оновлення конфігурації Odoo

Додати шлях до кастомних модулів в `odoo18.conf`:

```bash
# Редагувати конфігурацію
nano /www/wwwroot/odoo18-migration/odoo18.conf
```

Змінити рядок `addons_path`:
```ini
addons_path = /www/wwwroot/odoo18-migration/odoo/addons,/www/wwwroot/odoo18-migration/OpenUpgrade,/www/wwwroot/odoo18-migration/custom_addons
```

### 2. Клонування репозиторію з модулями

```bash
# Перейти в директорію Odoo
cd /www/wwwroot/odoo18-migration

# Клонувати репозиторій (замінити URL)
git clone [REPOSITORY_URL] custom_addons

# Перейти в директорію модулів
cd custom_addons

# Переключитися на гілку міграції
git checkout odoo18-migration
```

### 3. Копіювання скрипта деплою

```bash
# Створити директорію для скриптів
mkdir -p /www/wwwroot/odoo18-migration/scripts

# Скопіювати скрипт
cp server_deploy.sh /www/wwwroot/odoo18-migration/scripts/

# Надати права на виконання
chmod +x /www/wwwroot/odoo18-migration/scripts/server_deploy.sh

# Створити симлінк для зручності
ln -s /www/wwwroot/odoo18-migration/scripts/server_deploy.sh /usr/local/bin/odoo-deploy
```

---

## 🚀 Команди деплою

### Використання скрипта

```bash
# Показати довідку
odoo-deploy help

# Завантажити зміни з git
odoo-deploy pull

# Оновити конкретний модуль
odoo-deploy update mobius_lead_condition

# Оновити всі кастомні модулі
odoo-deploy update-all

# Встановити новий модуль
odoo-deploy install mobius_new_module

# Перезапустити сервіс
odoo-deploy restart

# Показати статус
odoo-deploy status

# Показати логи в реальному часі
odoo-deploy logs

# Створити бекап
odoo-deploy backup

# Відновити з бекапу
odoo-deploy restore odoo18_backup_20241216_120000.sql.gz

# Повний деплой (backup + pull + update-all + restart)
odoo-deploy deploy
```

---

## 📝 Ручні команди

### Git операції

```bash
# Перейти в директорію модулів
cd /www/wwwroot/odoo18-migration/custom_addons

# Перевірити статус
git status

# Завантажити зміни
git pull origin odoo18-migration

# Переглянути останні коміти
git log --oneline -10
```

### Odoo операції

```bash
# Перейти в директорію Odoo
cd /www/wwwroot/odoo18-migration

# Активувати віртуальне середовище
source venv/bin/activate

# Оновити модуль
python odoo/odoo-bin -c odoo18.conf -u module_name --stop-after-init

# Встановити модуль
python odoo/odoo-bin -c odoo18.conf -i module_name --stop-after-init

# Оновити всі модулі
python odoo/odoo-bin -c odoo18.conf -u all --stop-after-init

# Запустити Odoo вручну (для тестування)
python odoo/odoo-bin -c odoo18.conf --http-port=8018

# Деактивувати віртуальне середовище
deactivate
```

### Systemd операції

```bash
# Перезапуск сервісу
systemctl restart odoo18

# Зупинка сервісу
systemctl stop odoo18

# Запуск сервісу
systemctl start odoo18

# Статус сервісу
systemctl status odoo18

# Логи сервісу
journalctl -u odoo18 -f

# Логи за останню годину
journalctl -u odoo18 --since "1 hour ago"
```

### PostgreSQL операції

```bash
# Підключення до бази
psql -h localhost -p 5433 -U odoo -d odoo18

# Перевірка статусу модулів
psql -h localhost -p 5433 -U odoo -d odoo18 -c "SELECT name, state FROM ir_module_module WHERE name LIKE 'mobius%' ORDER BY name;"

# Активація модуля в БД
psql -h localhost -p 5433 -U odoo -d odoo18 -c "UPDATE ir_module_module SET state = 'to install' WHERE name = 'module_name';"

# Деактивація модуля в БД
psql -h localhost -p 5433 -U odoo -d odoo18 -c "UPDATE ir_module_module SET state = 'uninstalled' WHERE name = 'module_name';"

# Бекап бази
pg_dump -h localhost -p 5433 -U odoo -d odoo18 > backup.sql

# Відновлення бази
psql -h localhost -p 5433 -U odoo -d odoo18 < backup.sql
```

---

## 🔄 Типовий workflow деплою

### Після завершення міграції модуля в Claude Code:

```bash
# 1. На сервері: завантажити зміни
odoo-deploy pull

# 2. Перевірити що змінилося
cd /www/wwwroot/odoo18-migration/custom_addons
git log --oneline -5

# 3. Оновити конкретний модуль
odoo-deploy update mobius_module_name

# 4. Перевірити логи на помилки
cat /www/wwwroot/odoo18-migration/logs/update_mobius_module_name_*.log | grep -i error

# 5. Якщо все ок - перезапустити сервіс
odoo-deploy restart

# 6. Перевірити статус
odoo-deploy status
```

### Повний деплой (всі модулі):

```bash
# Автоматичний деплой з бекапом
odoo-deploy deploy
```

---

## ⚠️ Важливі примітки

### Перед деплоєм:
1. Завжди робити бекап бази даних
2. Перевіряти логи на помилки
3. Тестувати на staging якщо можливо

### При помилках:
1. Перевірити логи: `/www/wwwroot/odoo18-migration/logs/`
2. Перевірити журнал systemd: `journalctl -u odoo18 -n 100`
3. Відновити з бекапу якщо потрібно

### Порядок встановлення модулів:
1. Спочатку `mobius` (базовий модуль)
2. Потім залежні модулі за порядком

---

## 📁 Структура директорій

```
/www/wwwroot/odoo18-migration/
├── odoo/                    # Вихідний код Odoo 18
├── OpenUpgrade/             # Скрипти міграції
├── custom_addons/           # Кастомні модулі (git repo)
│   ├── mobius/
│   ├── mobius_*/
│   ├── l10n_ua/
│   └── ...
├── venv/                    # Python віртуальне середовище
├── filestore/               # Файли Odoo
│   └── odoo18/
├── scripts/                 # Скрипти деплою
│   └── server_deploy.sh
├── logs/                    # Логи оновлень
├── backups/                 # Бекапи БД
├── odoo18.conf              # Конфігурація
└── migration.log            # Лог міграції
```

---

## 🔧 Налагодження

### Проблема: Модуль не встановлюється

```bash
# Перевірити залежності
grep -A 10 "depends" /www/wwwroot/odoo18-migration/custom_addons/module_name/__manifest__.py

# Перевірити чи є помилки в Python
cd /www/wwwroot/odoo18-migration
source venv/bin/activate
python -c "import sys; sys.path.insert(0, 'custom_addons'); import module_name"
```

### Проблема: Помилки в XML views

```bash
# Знайти проблемні файли
grep -rn "<tree" custom_addons/module_name/ --include="*.xml"
grep -rn "colors=" custom_addons/module_name/ --include="*.xml"
```

### Проблема: Сервіс не запускається

```bash
# Детальні логи
journalctl -u odoo18 -n 200 --no-pager

# Спробувати запустити вручну
cd /www/wwwroot/odoo18-migration
source venv/bin/activate
python odoo/odoo-bin -c odoo18.conf --log-level=debug
```

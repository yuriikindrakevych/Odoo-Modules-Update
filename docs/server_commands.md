# Команди для деплою на сервер

## Інформація про сервер

- **Домен:** odoo-18.aclima.ua
- **Шлях:** /www/wwwroot/odoo-18.aclima.ua/
- **PostgreSQL порт:** 5432
- **База даних:** odoo18_new
- **HTTP порт:** 8069
- **Користувач:** deploy
- **Сервіс:** odoo18

---

## 🚀 Швидкі команди керування

```bash
# Статус сервісу
sudo systemctl status odoo18

# Перезапуск сервісу
sudo systemctl restart odoo18

# Зупинка сервісу
sudo systemctl stop odoo18

# Запуск сервісу
sudo systemctl start odoo18

# Логи в реальному часі
sudo journalctl -u odoo18 -f

# Логи за останню годину
sudo journalctl -u odoo18 --since "1 hour ago"
```

---

## 📋 Підготовка сервера

### 1. Оновлення конфігурації Odoo

Додати шлях до кастомних модулів в `odoo18.conf`:

```bash
# Редагувати конфігурацію
nano /www/wwwroot/odoo-18.aclima.ua/odoo18.conf
```

Змінити рядок `addons_path`:
```ini
addons_path = /www/wwwroot/odoo-18.aclima.ua/odoo/addons,/www/wwwroot/odoo-18.aclima.ua/OpenUpgrade,/www/wwwroot/odoo-18.aclima.ua/custom_addons
```

### 2. Клонування репозиторію з модулями

```bash
# Перейти в директорію Odoo
cd /www/wwwroot/odoo-18.aclima.ua

# Клонувати репозиторій (замінити URL)
git clone [REPOSITORY_URL] custom_addons

# Перейти в директорію модулів
cd custom_addons

# Переключитися на основну гілку
git checkout main
```

### 3. Копіювання скрипта деплою

```bash
# Створити директорію для скриптів
mkdir -p /www/wwwroot/odoo-18.aclima.ua/scripts

# Скопіювати скрипт
cp server_deploy.sh /www/wwwroot/odoo-18.aclima.ua/scripts/

# Надати права на виконання
chmod +x /www/wwwroot/odoo-18.aclima.ua/scripts/server_deploy.sh

# Створити симлінк для зручності
sudo ln -s /www/wwwroot/odoo-18.aclima.ua/scripts/server_deploy.sh /usr/local/bin/odoo-deploy
```

---

## 🚀 Команди деплою

### Використання скрипта

```bash
# Показати довідку
sudo odoo-deploy help

# Завантажити зміни з git
sudo odoo-deploy pull

# Оновити конкретний модуль
sudo odoo-deploy update mobius_lead_condition

# Оновити всі кастомні модулі
sudo odoo-deploy update-all

# Встановити новий модуль
sudo odoo-deploy install mobius_new_module

# Перезапустити сервіс
sudo odoo-deploy restart

# Показати статус
sudo odoo-deploy status

# Показати логи в реальному часі
sudo odoo-deploy logs

# Створити бекап
sudo odoo-deploy backup

# Відновити з бекапу
sudo odoo-deploy restore odoo18_backup_20241216_120000.sql.gz

# Повний деплой (backup + pull + update-all + restart)
sudo odoo-deploy deploy
```

---

## 📝 Ручні команди

### Git операції

```bash
# Перейти в директорію модулів
cd /www/wwwroot/odoo-18.aclima.ua/custom_addons

# Перевірити статус
git status

# Завантажити зміни
git pull origin main

# Переглянути останні коміти
git log --oneline -10
```

### Odoo операції

```bash
# Перейти в директорію Odoo
cd /www/wwwroot/odoo-18.aclima.ua

# Активувати віртуальне середовище
source venv/bin/activate

# Оновити модуль
python odoo/odoo-bin -c odoo18.conf -u module_name --stop-after-init

# Встановити модуль
python odoo/odoo-bin -c odoo18.conf -i module_name --stop-after-init

# Оновити всі модулі
python odoo/odoo-bin -c odoo18.conf -u all --stop-after-init

# Запустити Odoo вручну (для тестування)
python odoo/odoo-bin -c odoo18.conf --http-port=8069

# Деактивувати віртуальне середовище
deactivate
```

### Systemd операції

```bash
# Перезапуск сервісу
sudo systemctl restart odoo18

# Зупинка сервісу
sudo systemctl stop odoo18

# Запуск сервісу
sudo systemctl start odoo18

# Статус сервісу
sudo systemctl status odoo18

# Увімкнути автозапуск
sudo systemctl enable odoo18

# Вимкнути автозапуск
sudo systemctl disable odoo18

# Логи сервісу
sudo journalctl -u odoo18 -f

# Логи за останню годину
sudo journalctl -u odoo18 --since "1 hour ago"

# Останні 100 рядків логів
sudo journalctl -u odoo18 -n 100 --no-pager
```

### PostgreSQL операції

```bash
# Підключення до бази
psql -h localhost -p 5432 -U odoo -d odoo18_new

# Перевірка статусу модулів
psql -h localhost -p 5432 -U odoo -d odoo18_new -c "SELECT name, state FROM ir_module_module WHERE name LIKE 'mobius%' ORDER BY name;"

# Активація модуля в БД
psql -h localhost -p 5432 -U odoo -d odoo18_new -c "UPDATE ir_module_module SET state = 'to install' WHERE name = 'module_name';"

# Деактивація модуля в БД
psql -h localhost -p 5432 -U odoo -d odoo18_new -c "UPDATE ir_module_module SET state = 'uninstalled' WHERE name = 'module_name';"

# Бекап бази
pg_dump -h localhost -p 5432 -U odoo -d odoo18_new > backup.sql

# Бекап бази (стиснутий)
pg_dump -h localhost -p 5432 -U odoo -d odoo18_new | gzip > backup.sql.gz

# Відновлення бази
psql -h localhost -p 5432 -U odoo -d odoo18_new < backup.sql
```

---

## 🔄 Типовий workflow деплою

### Після завершення міграції модуля в Claude Code:

```bash
# 1. На сервері: завантажити зміни
cd /www/wwwroot/odoo-18.aclima.ua/custom_addons
git pull origin main

# 2. Перевірити що змінилося
git log --oneline -5

# 3. Зупинити сервіс перед оновленням
sudo systemctl stop odoo18

# 4. Оновити конкретний модуль
cd /www/wwwroot/odoo-18.aclima.ua
source venv/bin/activate
python odoo/odoo-bin -c odoo18.conf -u mobius_module_name --stop-after-init

# 5. Запустити сервіс
sudo systemctl start odoo18

# 6. Перевірити статус
sudo systemctl status odoo18

# 7. Перевірити логи на помилки
sudo journalctl -u odoo18 -n 50 --no-pager
```

### Швидке оновлення (без зупинки сервісу):

```bash
# Якщо сервіс може бути перезапущений
cd /www/wwwroot/odoo-18.aclima.ua/custom_addons
git pull origin main
sudo systemctl restart odoo18
```

---

## ⚠️ Важливі примітки

### Перед деплоєм:
1. Завжди робити бекап бази даних
2. Перевіряти логи на помилки
3. Тестувати на staging якщо можливо

### При помилках:
1. Перевірити логи: `sudo journalctl -u odoo18 -n 100`
2. Перевірити чи запущений сервіс: `sudo systemctl status odoo18`
3. Спробувати запустити вручну для детальних помилок
4. Відновити з бекапу якщо потрібно

### Порядок встановлення модулів:
1. Спочатку `mobius` (базовий модуль)
2. Потім залежні модулі за порядком

---

## 📁 Структура директорій

```
/www/wwwroot/odoo-18.aclima.ua/
├── odoo/                    # Вихідний код Odoo 18
├── OpenUpgrade/             # Скрипти міграції
├── custom_addons/           # Кастомні модулі (git repo)
│   ├── mobius/
│   ├── mobius_*/
│   ├── l10n_ua/
│   └── ...
├── venv/                    # Python віртуальне середовище
├── filestore/               # Файли Odoo
│   └── odoo18_new/
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
grep -A 10 "depends" /www/wwwroot/odoo-18.aclima.ua/custom_addons/module_name/__manifest__.py

# Перевірити чи є помилки в Python
cd /www/wwwroot/odoo-18.aclima.ua
source venv/bin/activate
python -c "import sys; sys.path.insert(0, 'custom_addons'); import module_name"
```

### Проблема: Помилки в XML views

```bash
# Знайти проблемні файли
grep -rn "<tree" /www/wwwroot/odoo-18.aclima.ua/custom_addons/module_name/ --include="*.xml"
grep -rn "colors=" /www/wwwroot/odoo-18.aclima.ua/custom_addons/module_name/ --include="*.xml"
```

### Проблема: Сервіс не запускається

```bash
# Детальні логи
sudo journalctl -u odoo18 -n 200 --no-pager

# Спробувати запустити вручну
cd /www/wwwroot/odoo-18.aclima.ua
source venv/bin/activate
python odoo/odoo-bin -c odoo18.conf --log-level=debug
```

### Проблема: Порт зайнятий

```bash
# Знайти процес що займає порт
sudo lsof -i :8069

# Зупинити всі процеси Odoo
sudo pkill -9 -f odoo-bin

# Запустити сервіс
sudo systemctl start odoo18
```

---

## 🔐 Systemd сервіс

Файл сервісу: `/etc/systemd/system/odoo18.service`

```ini
[Unit]
Description=Odoo 18
After=network.target postgresql.service

[Service]
Type=simple
User=deploy
Group=deploy
ExecStart=/www/wwwroot/odoo-18.aclima.ua/venv/bin/python /www/wwwroot/odoo-18.aclima.ua/odoo/odoo-bin -c /www/wwwroot/odoo-18.aclima.ua/odoo18.conf --http-port=8069
WorkingDirectory=/www/wwwroot/odoo-18.aclima.ua
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Після змін в сервісі:
```bash
sudo systemctl daemon-reload
sudo systemctl restart odoo18
```

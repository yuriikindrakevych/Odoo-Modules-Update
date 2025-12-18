# Технічне завдання: Адаптація кастомних модулів Odoo для версії 18

## 🎯 ВАЖЛИВО: Git операції

**Перед початком роботи:**
```bash
# Клонувати репозиторій (посилання буде додано)
git clone [REPOSITORY_URL] /www/wwwroot/odoo18-migration/custom_addons

# Перейти в директорію
cd /www/wwwroot/odoo18-migration/custom_addons

# Створити та перейти на робочу гілку
git checkout -b odoo18-migration
```

**Після кожного завершеного модуля:**
```bash
git add .
git commit -m "Migrate [module_name] to Odoo 18"
git push origin odoo18-migration
```

**REPOSITORY_URL:** _[ВСТАВИТИ ПОСИЛАННЯ НА ПРИВАТНИЙ РЕПОЗИТОРІЙ]_

---

## 📋 Огляд проєкту

### Контекст
Виконано міграцію бази даних Odoo з версії 15 до 18 через OpenUpgrade (15→16→17→18). Кастомні модулі були деактивовані під час міграції та потребують адаптації для Odoo 18.

### Мета
Адаптувати всі кастомні модулі (mobius_*, l10n_ua, account_dynamic_reports, base_account_budget, base_api, openapi) для сумісності з Odoo 18.

### Розташування
- **Odoo 18:** `/www/wwwroot/odoo18-migration/odoo/`
- **OpenUpgrade:** `/www/wwwroot/odoo18-migration/OpenUpgrade/`
- **Кастомні модулі:** `/www/wwwroot/odoo18-migration/custom_addons/`
- **Конфігурація:** `/www/wwwroot/odoo18-migration/odoo18.conf`
- **PostgreSQL:** `localhost:5433`, user: `odoo`, password: `odoo`, database: `odoo18`

---

## 🔄 Ключові зміни Odoo 15 → 18

### 1. ORM API зміни

#### Deprecated/Removed методи
```python
# ❌ СТАРИЙ КОД (Odoo 15)
@api.multi
def some_method(self):
    pass

@api.one
def another_method(self):
    pass

def name_get(self):
    return [(rec.id, rec.name) for rec in self]

# ✅ НОВИЙ КОД (Odoo 18)
def some_method(self):
    for record in self:
        pass

def another_method(self):
    self.ensure_one()
    pass

# name_get() deprecated - використовувати display_name або _compute_display_name
```

#### Нова сигнатура _read_group()
```python
# ❌ СТАРИЙ КОД
result = self._read_group(
    domain=[],
    fields=['field1', 'field2:sum'],
    groupby=['field3']
)

# ✅ НОВИЙ КОД (Odoo 17+)
result = self._read_group(
    domain=[],
    groupby=['field3'],
    aggregates=['field1:sum', 'field2:count']
)
```

#### Параметр args → domain
```python
# ❌ СТАРИЙ КОД
def search(self, args, offset=0, limit=None):
    pass

# ✅ НОВИЙ КОД
def search(self, domain, offset=0, limit=None):
    pass
```

#### group_operator → aggregator
```python
# ❌ СТАРИЙ КОД
field = fields.Float(group_operator='sum')

# ✅ НОВИЙ КОД
field = fields.Float(aggregator='sum')
```

#### Нові методи пошуку
```python
# Нові методи в Odoo 17+
records = self.search_fetch(domain, ['field1', 'field2'])  # search + read
records.fetch(['field1', 'field2'])  # prefetch fields
```

#### SQL wrapper
```python
# ❌ СТАРИЙ КОД
self.env.cr.execute("SELECT * FROM table WHERE id IN %s", (tuple(ids),))

# ✅ НОВИЙ КОД (рекомендований)
from odoo.osv.expression import SQL
query = SQL("SELECT * FROM table WHERE id IN %s", tuple(ids))
self.env.cr.execute(query)
```

### 2. Fields зміни

#### Видалені атрибути
```python
# ❌ Видалено в Odoo 17+
field = fields.One2many(limit=100)  # limit видалено
field = fields.Many2many(limit=50)  # limit видалено

# ❌ Видалено
_sequence = 'custom_sequence'  # атрибут моделі видалено
```

#### Translated fields
```python
# Переклади тепер зберігаються як JSONB в базі даних
# Перевірити сумісність translated=True полів
```

### 3. XML Views зміни

#### tree → list (Odoo 17+)
```xml
<!-- ❌ СТАРИЙ КОД -->
<record id="view_tree" model="ir.ui.view">
    <field name="arch" type="xml">
        <tree string="Records">
            ...
        </tree>
    </field>
</record>

<!-- ✅ НОВИЙ КОД -->
<record id="view_tree" model="ir.ui.view">
    <field name="arch" type="xml">
        <list string="Records">
            ...
        </list>
    </field>
</record>
```

#### Deprecated атрибути
```xml
<!-- ❌ Видалено -->
<tree colors="...">  <!-- colors deprecated, використовувати decoration-* -->
<tree fonts="...">   <!-- fonts deprecated -->

<!-- ✅ НОВИЙ КОД -->
<list decoration-danger="state == 'cancel'"
      decoration-success="state == 'done'">
```

#### Kanban views
```xml
<!-- ❌ СТАРИЙ КОД -->
<kanban>
    <templates>
        <t t-name="kanban-box">
            ...
        </t>
    </templates>
</kanban>

<!-- ✅ НОВИЙ КОД (Odoo 18+) -->
<kanban>
    <templates>
        <t t-name="card">
            ...
        </t>
    </templates>
</kanban>
```

### 4. __manifest__.py зміни

#### Версія модуля
```python
# ❌ СТАРИЙ КОД
{
    'version': '15.0.1.0.0',
}

# ✅ НОВИЙ КОД
{
    'version': '18.0.1.0.0',
}
```

#### Assets замість qweb
```python
# ❌ СТАРИЙ КОД (до Odoo 15)
{
    'qweb': [
        'static/src/xml/template.xml',
    ],
}

# ✅ НОВИЙ КОД (Odoo 15+)
{
    'assets': {
        'web.assets_backend': [
            'module_name/static/src/js/file.js',
            'module_name/static/src/scss/file.scss',
        ],
        'web.assets_qweb': [
            'module_name/static/src/xml/template.xml',
        ],
    },
}
```

### 5. JavaScript зміни

#### ES6 модулі
```javascript
// ❌ СТАРИЙ КОД
odoo.define('module.widget', function (require) {
    var Widget = require('web.Widget');
    // ...
});

// ✅ НОВИЙ КОД
/** @odoo-module **/
import { Component } from "@odoo/owl";
// або
import { Widget } from "@web/views/widgets/widget";
```

#### OWL Framework
```javascript
// Odoo 17+ використовує OWL 2.x
// Перевірити сумісність компонентів з новою версією OWL
```

### 6. Security зміни

#### Нова структура груп
```python
# Перевірити group_ids в ir.ui.menu та ir.rule
# Можливі зміни в стандартних групах Odoo
```

### 7. HTTP Routes
```python
# ❌ СТАРИЙ КОД
@http.route('/api/data', type='json')

# ✅ НОВИЙ КОД (Odoo 18+)
@http.route('/api/data', type='jsonrpc')  # type='json' renamed to 'jsonrpc'
```

---

## 📝 Алгоритм адаптації модуля

### Крок 1: Аналіз модуля
```bash
# Перейти в директорію модуля
cd /www/wwwroot/odoo18-migration/custom_addons/[module_name]

# Переглянути структуру
ls -la

# Знайти deprecated код
grep -rn "@api.multi" .
grep -rn "@api.one" .
grep -rn "name_get" .
grep -rn "<tree" . --include="*.xml"
grep -rn "group_operator" .
grep -rn "type='json'" . --include="*.py"
```

### Крок 2: Оновлення __manifest__.py
1. Змінити версію на `18.0.x.x.x`
2. Перевірити/оновити залежності
3. Перенести `qweb` в `assets`
4. Додати `license` якщо відсутній

### Крок 3: Оновлення Python коду
1. Видалити `@api.multi`, `@api.one`
2. Замінити `name_get()` на `_compute_display_name()`
3. Оновити `_read_group()` сигнатуру
4. Замінити `group_operator` на `aggregator`
5. Оновити SQL запити з SQL wrapper
6. Перевірити успадковані моделі на зміни в базових класах

### Крок 4: Оновлення XML
1. Замінити `<tree>` на `<list>`
2. Замінити `colors` на `decoration-*`
3. Оновити kanban `<kanban-box>` на `<card>` (якщо Odoo 18)
4. Перевірити xpath виразі на зміни в базових view

### Крок 5: Оновлення JavaScript (якщо є)
1. Перевірити на deprecated require()
2. Оновити до ES6 модулів з `/** @odoo-module **/`
3. Перевірити OWL компоненти

### Крок 6: Тестування
```bash
# Оновити модуль
cd /www/wwwroot/odoo18-migration
source venv/bin/activate
python odoo/odoo-bin -c odoo18.conf -u [module_name] --stop-after-init --log-level=info 2>&1 | tee update_[module_name].log

# Перевірити на помилки
grep -i "error" update_[module_name].log
grep -i "warning" update_[module_name].log
```

### Крок 7: Git commit
```bash
cd /www/wwwroot/odoo18-migration/custom_addons
git add [module_name]/
git commit -m "Migrate [module_name] to Odoo 18

Changes:
- Updated manifest version to 18.0
- Removed deprecated @api.multi/@api.one decorators
- Replaced <tree> with <list> in XML views
- [other specific changes]
"
git push origin odoo18-migration
```

---

## ⚠️ Особливі випадки

### CRM модулі (mobius_crm_*, mobius_lead_*)
- Перевірити зміни в `crm.lead` моделі
- `stage_id` може мати нові поля
- Перевірити workflow активностей

### Sale Order модулі (mobius_sale_order_*)
- Перевірити зміни в `sale.order` та `sale.order.line`
- `product_uom` → `product_uom_id` (можливо)
- Перевірити downpayment логіку

### Portal модулі (mobius_portal_*, mobius_registration_*)
- Перевірити зміни в portal controllers
- Website templates можуть мати нову структуру

### API модулі (openapi, base_api, mobius_login_screen_api)
- `type='json'` → `type='jsonrpc'`
- Перевірити auth методи
- Перевірити CORS налаштування

### Accounting модулі (account_dynamic_reports, base_account_budget)
- Значні зміни в account модулях між версіями
- Перевірити report структуру
- Аналітичні рахунки змінили структуру в v16+

### Ukrainian localization (l10n_ua)
- Перевірити chart of accounts
- Перевірити tax templates
- Можливо потрібне порівняння з офіційним l10n_ua для v18

---

## 📊 Критерії завершення

Модуль вважається адаптованим коли:
1. ✅ `__manifest__.py` має версію `18.0.x.x.x`
2. ✅ Модуль встановлюється без помилок
3. ✅ Модуль оновлюється без помилок
4. ✅ Немає deprecated warnings в логах
5. ✅ Базова функціональність працює
6. ✅ Зміни закомічені та запушені

---

## 🔗 Корисні посилання

- [Odoo 18 ORM Changelog](https://www.odoo.com/documentation/18.0/developer/reference/backend/orm/changelog.html)
- [Odoo 18 Developer Documentation](https://www.odoo.com/documentation/18.0/developer.html)
- [OCA OpenUpgrade](https://github.com/OCA/OpenUpgrade)
- [OCA Module Migrator](https://github.com/OCA/odoo-module-migrator)

---

## 📁 Структура репозиторію

```
custom_addons/
├── mobius/
├── mobius_activity_reports/
├── mobius_advanced_calendar_aklima/
├── ... (інші модулі)
├── l10n_ua/
├── account_dynamic_reports/
├── base_account_budget/
├── base_api/
└── openapi/
```

---

## 🚀 Порядок міграції

Рекомендований порядок (від простих до складних):
1. **Базові/прості модулі** - мінімальні залежності
2. **CRM/Lead модулі** - середня складність
3. **Sale Order модулі** - середня складність  
4. **Portal/Website модулі** - можуть мати JS
5. **API модулі** - потребують тестування endpoints
6. **Accounting модулі** - найскладніші, значні зміни

Детальний список див. у `modules_list.md`

---

## 🖥️ Деплой модулів на сервер для тестування

### Розташування на сервері

```
/www/wwwroot/odoo18-migration/
├── odoo/                    # Odoo 18 source code
├── OpenUpgrade/             # OpenUpgrade (використовувався для міграції)
├── custom_addons/           # ← СЮДИ ЗАЛИВАТИ МОДУЛІ
├── venv/                    # Python virtual environment
├── logs/                    # Логи
└── odoo18.conf              # Конфігурація Odoo
```

**Директорія для модулів:** `/www/wwwroot/odoo18-migration/custom_addons/`

### Перевірка конфігурації Odoo

Переконайтеся, що в `odoo18.conf` вказано шлях до `custom_addons`:

```bash
# Переглянути конфігурацію
cat /www/wwwroot/odoo18-migration/odoo18.conf | grep addons_path
```

Має бути щось типу:
```ini
addons_path = /www/wwwroot/odoo18-migration/odoo/addons,/www/wwwroot/odoo18-migration/custom_addons
```

Якщо `custom_addons` не вказано, додайте його:
```bash
nano /www/wwwroot/odoo18-migration/odoo18.conf
# Додати custom_addons до addons_path
```

---

## 🔄 Заміна старих модулів на нові

### Ситуація: Модулі вже є на сервері, але вимкнені

Якщо кастомні модулі вже є в `custom_addons/`, але вони були деактивовані під час міграції через OpenUpgrade:

#### Варіант 1: Оновлення через Git (рекомендовано)

```bash
# Перейти в директорію модулів
cd /www/wwwroot/odoo18-migration/custom_addons

# Перевірити статус git
git status

# Якщо є локальні зміни, зберегти їх
git stash

# Отримати останню версію з GitHub
git fetch origin main
git checkout main
git pull origin main

# Якщо потрібно відновити локальні зміни
git stash pop
```

#### Варіант 2: Повна заміна директорії

```bash
# 1. Зробити бекап старих модулів (на всяк випадок)
cd /www/wwwroot/odoo18-migration
sudo mv custom_addons custom_addons_backup_$(date +%Y%m%d)

# 2. Клонувати репозиторій з оновленими модулями
git clone https://github.com/yuriikindrakevych/Odoo-Modules-Update.git custom_addons

# 3. Перевірити структуру
ls -la custom_addons/
```

#### Варіант 3: Вибіркова заміна модулів

```bash
cd /www/wwwroot/odoo18-migration/custom_addons

# Для кожного модуля окремо:

# 1. Видалити старий модуль
sudo rm -rf mobius_lead_condition/

# 2. Скопіювати новий модуль з локальної машини
# (або використати git для окремого модуля)
scp -r user@local:/path/to/mobius_lead_condition/ ./

# АБО через git sparse checkout
git fetch origin main
git checkout origin/main -- mobius_lead_condition/
```

---

## ⚠️ ВАЖЛИВО: Послідовність дій після заміни модулів

### Крок 1: Перезапустити Odoo для оновлення списку модулів

```bash
# Зупинити Odoo
sudo systemctl stop odoo18
# або
sudo supervisorctl stop odoo18

# Запустити Odoo
sudo systemctl start odoo18
# або
sudo supervisorctl start odoo18
```

### Крок 2: Оновити список модулів в інтерфейсі

1. Зайти в Odoo як адмін
2. Перейти в **Settings** → **Apps**
3. Натиснути **Update Apps List** (або "Оновити список застосунків")
4. Підтвердити оновлення

### Крок 3: Встановити/оновити модулі

#### Через командний рядок (рекомендовано для тестування):

```bash
cd /www/wwwroot/odoo18-migration
source venv/bin/activate

# Оновити один модуль
python odoo/odoo-bin -c odoo18.conf -u mobius_lead_condition --stop-after-init

# Оновити кілька модулів
python odoo/odoo-bin -c odoo18.conf -u mobius,mobius_lead_condition,mobius_crm_customization --stop-after-init

# Встановити новий модуль
python odoo/odoo-bin -c odoo18.conf -i mobius_new_module --stop-after-init
```

#### Через веб-інтерфейс:

1. **Settings** → **Apps**
2. Зняти фільтр "Apps" (показати всі модулі)
3. Знайти потрібний модуль
4. Натиснути **Install** або **Upgrade**

---

## 🧹 Видалення непотрібних модулів

### Модулі з коробковою заміною в Odoo 18

Ці модулі можна видалити, якщо їх функціонал вже є в стандартному Odoo 18:

```bash
cd /www/wwwroot/odoo18-migration/custom_addons

# Перед видаленням переконайтеся, що модуль деінстальований в Odoo!
# Видалення встановленого модуля може пошкодити БД

# Приклад видалення (ТІЛЬКИ якщо модуль деінстальований):
rm -rf base_account_budget/      # Замінено на account_budget (Enterprise)
rm -rf mail_debrand/             # Замінено на System Parameters
```

### Перевірка стану модуля перед видаленням

```bash
# Підключитися до PostgreSQL
psql -h localhost -p 5433 -U odoo -d odoo18

# Перевірити стан модуля
SELECT name, state FROM ir_module_module WHERE name = 'module_name';

# Має бути 'uninstalled' для безпечного видалення
```

---

## 📋 Чек-лист деплою

- [ ] Зробити бекап бази даних перед оновленням
- [ ] Оновити/замінити модулі в `custom_addons/`
- [ ] Перевірити `addons_path` в `odoo18.conf`
- [ ] Перезапустити Odoo сервіс
- [ ] Оновити список модулів в інтерфейсі
- [ ] Запустити скрипт аналізу `analyze_modules.sh`
- [ ] Встановити модулі по черзі (спочатку базові)
- [ ] Перевірити логи на помилки
- [ ] Протестувати функціонал

---

## 🆘 Відновлення у разі проблем

```bash
# Якщо щось пішло не так - відновлення з бекапу

# 1. Зупинити Odoo
sudo systemctl stop odoo18

# 2. Відновити модулі з бекапу
cd /www/wwwroot/odoo18-migration
rm -rf custom_addons
mv custom_addons_backup_YYYYMMDD custom_addons

# 3. Відновити базу даних (якщо потрібно)
dropdb -h localhost -p 5433 -U odoo odoo18
createdb -h localhost -p 5433 -U odoo odoo18
pg_restore -h localhost -p 5433 -U odoo -d odoo18 /path/to/backup.dump

# 4. Запустити Odoo
sudo systemctl start odoo18
```

# TODO: План адаптації модулів Odoo 18

## 🎯 Загальний прогрес
- [x] **Фаза 0:** Підготовка проекту (завершено)
- [x] **Фаза 1:** Базові модулі (16/16) ✅
- [x] **Фаза 2:** Середня складність (18/18) ✅
- [x] **Фаза 3:** Висока складність + додаткові (25/25) ✅

**ВСЬОГО МІГРОВАНО: 59 модулів** 🎉

---

## ✅ Фаза 0: Підготовка проекту (ЗАВЕРШЕНО)

**Дата:** 2024-12-17

### Виконані роботи:
- [x] Завантажено бекап з сервера (`odoo_full_backup_20251217`)
- [x] Знайдено кастомні модулі в `addons-custom/` (14 модулів) та `addons-dev/` (45 модулів)
- [x] Скопійовано всі 59 модулів в кореневу папку проекту
- [x] Видалено зайві файли Odoo (`odoo18-migration/`, `odoo_full_backup_20251217/`)
- [x] Створено `.gitignore` для ігнорування IDE файлів
- [x] Зроблено git commit та push в GitHub

### Структура модулів:

**Mobius модулі (49):**
- `mobius` (базовий)
- `mobius_activity_reports`, `mobius_advanced_calendar_aklima`, `mobius_aklima_custom`
- `mobius_aklima_import_lead`, `mobius_auto_login`, `mobius_automatic_delivery_sale_order`
- `mobius_bulding_object`, `mobius_catalogue_koatuu`, `mobius_check_balanced_off`
- `mobius_choose_reason_loss_lead`, `mobius_contact_and_lead_search`, `mobius_contact_by_vat`
- `mobius_contact_form_aklima`, `mobius_contact_priority`, `mobius_creating_invoice_after_down_payment_aklima`
- `mobius_crm_customization`, `mobius_crm_lead_advanced_import`, `mobius_custom_sales_team_autofill`
- `mobius_email_to_inbox`, `mobius_google_sheet_importer`, `mobius_inventory_supplier`
- `mobius_lead_by_vat`, `mobius_lead_condition`, `mobius_lead_contact_import`
- `mobius_lead_from_api`, `mobius_lead_today_task_aklima`, `mobius_login_screen_api`
- `mobius_portal_aklima`, `mobius_portal_user_correct_pricelist`, `mobius_product_category_attributes`
- `mobius_product_sizes`, `mobius_quotation_cancel_reason`, `mobius_registration_aklima`
- `mobius_rel_lead_and_contact_from_calendar`, `mobius_replace_mail_bounce_catchall_aklima`
- `mobius_sale_order_convert`, `mobius_sale_order_counter`, `mobius_sale_order_downpayment_aklima`
- `mobius_sale_order_opportunity`, `mobius_sale_order_reports`, `mobius_sales_follower`
- `mobius_skip_check_balanced`, `mobius_translate_account_aklima`, `mobius_translate_polish_szanse`
- `mobius_translate_website_aklima`, `mobius_translate_website_sale_stock_aklima`, `mobius_turbosms`
- `mobius_website_product_sharelink_hide`

**Сторонні/OCA модулі (10):**
- `account_dynamic_reports`, `account_netting`, `barcodes_generator_abstract`
- `base_account_budget`, `base_accounting_kit`, `base_api`
- `crm_facebook_leads`, `google_sheet_importer`, `mail_debrand`, `openapi`

---

## ✅ Фаза 1: Базові модулі (ЗАВЕРШЕНО)

**Дата:** 2024-12-18

### Виконані роботи:
- [x] Оновлено всі `__manifest__.py` до версії 18.0.x.x.x
- [x] Замінено `group_operator` на `aggregator` (mobius/models/res_currency.py)
- [x] Замінено `<tree>` на `<list>` в XML views
- [x] Замінено `view_mode="tree"` на `view_mode="list"`
- [x] Git commit та push

### Модулі (16):
| # | Модуль | Версія | Зміни |
|---|--------|--------|-------|
| 1 | `mobius` | 18.0.0.3 | group_operator→aggregator, tree→list |
| 2 | `mobius_contact_priority` | 18.0.0.0.1 | версія |
| 3 | `mobius_contact_by_vat` | 18.0.1.0.0 | версія |
| 4 | `mobius_lead_by_vat` | 18.0.0.1.2 | версія |
| 5 | `mobius_lead_condition` | 18.0.0.0.5 | tree→list, view_mode |
| 6 | `mobius_choose_reason_loss_lead` | 18.0.1.0.0 | версія |
| 7 | `mobius_product_sizes` | 18.0.1.0.0 | версія |
| 8 | `mobius_quotation_cancel_reason` | 18.0.0.4 | версія |
| 9 | `mobius_sale_order_counter` | 18.0.1.0.1 | версія |
| 10 | `mobius_sale_order_opportunity` | 18.0.1.0.1 | версія |
| 11 | `mobius_sales_follower` | 18.0.0.0.1 | версія |
| 12 | `mobius_custom_sales_team_autofill` | 18.0.0.1.0 | tree→list |
| 13 | `mobius_skip_check_balanced` | 18.0.1.0.0 | версія |
| 14 | `mobius_translate_polish_szanse` | 18.0.1.0.2 | версія |
| 15 | `mobius_replace_mail_bounce_catchall_aklima` | 18.0.1.0.0 | версія |
| 16 | `mobius_website_product_sharelink_hide` | 18.0.0.0.1 | версія |

---

## ✅ Фаза 2: Середня складність (ЗАВЕРШЕНО)

**Дата:** 2024-12-18

### Виконані роботи:
- [x] Оновлено всі `__manifest__.py` до версії 18.0.x.x.x
- [x] Замінено `<tree>` на `<list>` в 14 XML файлах
- [x] Замінено `view_mode="tree"` на `view_mode="list"`
- [x] Git commit та push

### Модулі (18):
| # | Модуль | Версія |
|---|--------|--------|
| 17 | `mobius_contact_form_aklima` | 18.0.0.0.2 |
| 18 | `mobius_contact_and_lead_search` | 18.0.0.0.2 |
| 19 | `mobius_lead_contact_import` | 18.0.0.1.5 |
| 20 | `mobius_crm_lead_advanced_import` | 18.0.0.0.3 |
| 21 | `mobius_lead_from_api` | 18.0.0.1.4 |
| 22 | `mobius_automatic_delivery_sale_order` | 18.0.1.0.0 |
| 23 | `mobius_sale_order_convert` | 18.0.1.0.0 |
| 24 | `mobius_sale_order_downpayment_aklima` | 18.0.1.0.4 |
| 25 | `mobius_creating_invoice_after_down_payment_aklima` | 18.0.0.0.0 |
| 26 | `mobius_sale_order_reports` | 18.0.0.3.3 |
| 27 | `mobius_inventory_supplier` | 18.0.1.0.0 |
| 28 | `mobius_activity_reports` | 18.0.1.0.1 |
| 29 | `mobius_advanced_calendar_aklima` | 18.0.0.1 |
| 30 | `mobius_rel_lead_and_contact_from_calendar` | 18.0.0.0.5 |
| 31 | `mobius_portal_user_correct_pricelist` | 18.0.0.1 |
| 32 | `mobius_catalogue_koatuu` | 18.0.0.0.3 |
| 33 | `mobius_aklima_custom` | 18.0.0.2.7 |
| 34 | `base_api` | 18.0.1.0.1 |

---

## ✅ Фаза 3: Висока складність + Додаткові модулі (ЗАВЕРШЕНО)

**Дата:** 2024-12-18

### Виконані роботи:
- [x] Оновлено всі `__manifest__.py` до версії 18.0.x.x.x
- [x] Замінено `<tree>` на `<list>` в усіх XML views
- [x] Замінено `view_mode="tree"` на `view_mode="list"`
- [x] Замінено `type='json'` на `type='jsonrpc'` в HTTP routes
- [x] Git commit та push

### Модулі Фази 3 (5):
| # | Модуль | Версія |
|---|--------|--------|
| 35 | `mobius_portal_aklima` | 18.0.0.1.6 |
| 36 | `mobius_registration_aklima` | 18.0.0.0.1 |
| 37 | `openapi` | 18.0.1.2.5 |
| 38 | `base_account_budget` | 18.0.1.1.0 |
| 39 | `account_dynamic_reports` | 18.0.1.0 |

### Додаткові модулі (20):
| # | Модуль | Версія |
|---|--------|--------|
| 40 | `account_netting` | 18.0.1.0.0 |
| 41 | `barcodes_generator_abstract` | 18.0.1.0.1 |
| 42 | `base_accounting_kit` | 18.0.2.2.2 |
| 43 | `crm_facebook_leads` | 18.0.2.0.1 |
| 44 | `google_sheet_importer` | 18.0.1.0.0 |
| 45 | `mail_debrand` | 18.0.1.0.0 |
| 46 | `mobius_aklima_import_lead` | 18.0.1.5.0 |
| 47 | `mobius_auto_login` | 18.0.1.0 |
| 48 | `mobius_bulding_object` | 18.0.0.12 |
| 49 | `mobius_check_balanced_off` | 18.0.1.0.0 |
| 50 | `mobius_crm_customization` | 18.0.0.1.1 |
| 51 | `mobius_email_to_inbox` | 18.0.1.0.1 |
| 52 | `mobius_google_sheet_importer` | 18.0.1.0.0 |
| 53 | `mobius_lead_today_task_aklima` | 18.0.0.1 |
| 54 | `mobius_login_screen_api` | 18.0.0.6 |
| 55 | `mobius_product_category_attributes` | 18.0.0.1 |
| 56 | `mobius_translate_account_aklima` | 18.0.0.1 |
| 57 | `mobius_translate_website_aklima` | 18.0.0.1 |
| 58 | `mobius_translate_website_sale_stock_aklima` | 18.0.0.1 |
| 59 | `mobius_turbosms` | 18.0.0.1 |

---

## ✅ Інструменти аналізу (ЗАВЕРШЕНО)

**Дата:** 2024-12-18

Створено скрипти для аналізу модулів перед встановленням:

### scripts/analyze_modules.sh (Серверний)
Скрипт для запуску на сервері з підключенням до PostgreSQL:
- Перевірка стану модуля в базі даних (installed/uninstalled)
- Підрахунок записів у таблицях модуля
- Аналіз залежностей між модулями
- Визначення коробкових замін в Odoo 18
- Генерація детального звіту `analysis_report_YYYYMMDD.md`

**Використання:**
```bash
cd /www/wwwroot/odoo18-migration/custom_addons
chmod +x scripts/analyze_modules.sh
./scripts/analyze_modules.sh
```

### scripts/analyze_code_local.sh (Локальний)
Скрипт для локального аналізу без підключення до БД:
- Аналіз Python коду (моделі, контролери, wizards)
- Аналіз XML (views, actions, menus, security)
- Перевірка JavaScript/OWL компонентів
- Виявлення legacy `odoo.define()` коду
- Mermaid граф залежностей
- Рекомендації порядку встановлення

**Використання:**
```bash
cd /media/yurii/Data\ 1/PhpStormProjects/Odoo-Modules-Update
chmod +x scripts/analyze_code_local.sh
./scripts/analyze_code_local.sh
```

### Коробкові заміни в Odoo 18:
| Модуль | Заміна |
|--------|--------|
| `base_account_budget` | account_budget (Enterprise) |
| `account_dynamic_reports` | Вбудовані динамічні звіти |
| `base_accounting_kit` | Стандартний Accounting модуль |
| `crm_facebook_leads` | Social Marketing (Enterprise) |
| `openapi` | Вбудований REST API (Odoo 17+) |
| `base_api` | JSON-RPC та REST API |
| `mail_debrand` | System Parameters |
| `barcodes_generator_abstract` | Покращений barcode модуль |
| `account_netting` | OCA/account-financial-tools |

---

## ⏳ Завершальні кроки

- [x] Оновлення `odoo18.conf` з шляхом до custom_addons
- [x] Клонування репозиторію на сервер
- [x] Встановлення базових модулів (mobius, mobius_lead_condition, etc.)
- [ ] Виправити модуль `mobius_portal_aklima` (багато XML templates потребують оновлення)
- [ ] Встановити решту модулів через інтерфейс Odoo
- [ ] Тестування взаємодії модулів
- [ ] Деплой на production

---

## ✅ Виправлення Odoo 18 (2024-12-22)

### Виправлені проблеми сумісності:

| Модуль | Проблема | Рішення |
|--------|----------|---------|
| `mobius_auto_login` | `main.Home` не існує | Імпорт з `odoo.addons.web.controllers.home` |
| `mobius_auto_login` | `main.ensure_db()` не існує | Імпорт з `odoo.addons.web.controllers.utils` |
| `mobius_auto_login` | Старий формат ir.cron | Новий формат без `numbercall`, `model_id`, `state` |
| `mobius` | Старий формат ir.cron | Аналогічно |
| `mobius_portal_aklima` | Залежність `sale_product_configurator` | Видалено (не існує в Odoo 18) |
| `mobius_portal_aklima` | Залежність `website_sale_delivery` | Видалено (не існує в Odoo 18) |
| `mobius_portal_aklima` | `_message_post_helper` не існує | Створено helper функцію |
| `mobius_portal_aklima` | `url_for` імпорт | Видалено невикористаний імпорт |
| `mobius_portal_aklima` | `type='jsonrpc'` | Замінено на `type='json'` |
| `mobius_portal_aklima` | `acquirer_id` | Замінено на `provider_id` |
| `mobius_portal_aklima` | XML templates (transaction_status, reduction_code, short_cart_summary) | Закоментовано (структура змінилась) |
| `mobius_automatic_delivery_sale_order` | Залежність `website_sale_delivery` | Видалено |
| `mobius_custom_sales_team_autofill` | `partner_id.team_id` в @depends | Замінено на `partner_id` + getattr |
| `mobius_quotation_cancel_reason` | Залежність `mobius_portal_aklima` | Видалено |
| `mobius_email_to_inbox` | Версія `15.0.1.0.1` | Оновлено до `18.0.1.0.1` |

### Модулі що потребують додаткової роботи:

1. **mobius_portal_aklima** - багато XML templates наслідують від templates що змінились в Odoo 18:
   - `website_sale.products_item`
   - `website_sale.product_price`
   - `sale_product_configurator.configure_optional_products`
   - `website_sale_delivery.*`
   - `website_sale.total`

---

## 📝 Нотатки

### Виявлені проблеми
1. База даних називається `odoo18_new`, не `odoo18`
2. PostgreSQL на порті 5433
3. Користувач з id=37 мав 2 типи користувача (Portal + Internal) - конфлікт constraint

### Рішення
1. Оновити `DB_NAME` в скриптах
2. Видалити зайву групу: `DELETE FROM res_groups_users_rel WHERE uid = 37 AND gid = 9;` 

### Корисні команди

```bash
# Швидка перевірка на deprecated код
grep -rn "@api.multi\|@api.one\|name_get\|<tree\|group_operator" module_name/

# Тестування модуля
cd /www/wwwroot/odoo18-migration
source venv/bin/activate
python odoo/odoo-bin -c odoo18.conf -u module_name --stop-after-init 2>&1 | tee test.log

# Git операції
cd /www/wwwroot/odoo18-migration/custom_addons
git status
git add module_name/
git commit -m "Migrate module_name to Odoo 18"
git push origin odoo18-migration
```

---

**Останнє оновлення:** _(автоматично оновлювати)_

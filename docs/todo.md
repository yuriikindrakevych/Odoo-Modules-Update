# TODO: План адаптації модулів Odoo 18

## 🎯 Загальний прогрес
- [x] **Фаза 0:** Підготовка проекту (завершено)
- [x] **Фаза 1:** Базові модулі (16/16) ✅
- [ ] **Фаза 2:** Середня складність (0/18)
- [ ] **Фаза 3:** Висока складність (0/6)

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

## 📋 Фаза 2: Середня складність

### 17. mobius_contact_form_aklima
- [ ] Аналіз структури модуля
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення Python коду
- [ ] Оновлення XML views
- [ ] Перевірка form controllers
- [ ] Тестування
- [ ] Git commit та push

### 18. mobius_contact_and_lead_search
- [ ] Аналіз структури модуля
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення Python коду
- [ ] Оновлення XML views
- [ ] Перевірка search методів
- [ ] Тестування
- [ ] Git commit та push

### 19. mobius_lead_contact_import
- [ ] Аналіз структури модуля
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення Python коду
- [ ] Оновлення import логіки
- [ ] Тестування імпорту
- [ ] Git commit та push

### 20. mobius_crm_lead_advanced_import
- [ ] Аналіз структури модуля
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення Python коду
- [ ] Оновлення import wizard
- [ ] Тестування імпорту
- [ ] Git commit та push

### 21. mobius_lead_from_api
- [ ] Аналіз структури модуля
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення API endpoints
- [ ] Заміна `type='json'` на `type='jsonrpc'`
- [ ] Тестування API
- [ ] Git commit та push

### 22. mobius_automatic_delivery_sale_order
- [ ] Аналіз структури модуля
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення Python коду
- [ ] Перевірка stock/delivery змін
- [ ] Тестування workflow
- [ ] Git commit та push

### 23. mobius_sale_order_convert
- [ ] Аналіз структури модуля
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення Python коду
- [ ] Перевірка sale.order змін
- [ ] Тестування конвертації
- [ ] Git commit та push

### 24. mobius_sale_order_downpayment_aklima
- [ ] Аналіз структури модуля
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення Python коду
- [ ] Перевірка downpayment логіки
- [ ] Тестування
- [ ] Git commit та push

### 25. mobius_creating_invoice_after_down_payment_aklima
- [ ] Аналіз структури модуля
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення Python коду
- [ ] Перевірка invoice creation
- [ ] Тестування
- [ ] Git commit та push

### 26. mobius_sale_order_reports
- [ ] Аналіз структури модуля
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення Python коду
- [ ] Оновлення report templates
- [ ] Тестування звітів
- [ ] Git commit та push

### 27. mobius_inventory_supplier
- [ ] Аналіз структури модуля
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення Python коду
- [ ] Перевірка stock змін
- [ ] Тестування
- [ ] Git commit та push

### 28. mobius_activity_reports
- [ ] Аналіз структури модуля
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення Python коду
- [ ] Оновлення _read_group() сигнатури
- [ ] Тестування звітів
- [ ] Git commit та push

### 29. mobius_advanced_calendar_aklima
- [ ] Аналіз структури модуля
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення Python коду
- [ ] Перевірка calendar змін
- [ ] Оновлення JavaScript (якщо є)
- [ ] Тестування
- [ ] Git commit та push

### 30. mobius_rel_lead_and_contact_from_calendar
- [ ] Аналіз структури модуля
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення Python коду
- [ ] Перевірка calendar/crm інтеграції
- [ ] Тестування
- [ ] Git commit та push

### 31. mobius_portal_user_correct_pricelist
- [ ] Аналіз структури модуля
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення Python коду
- [ ] Перевірка portal змін
- [ ] Тестування pricelist
- [ ] Git commit та push

### 32. mobius_catalogue_koatuu
- [ ] Аналіз структури модуля
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення Python коду
- [ ] Перевірка data files
- [ ] Тестування
- [ ] Git commit та push

### 33. mobius_aklima_custom
- [ ] Аналіз структури модуля
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення Python коду
- [ ] Оновлення всіх views
- [ ] Тестування
- [ ] Git commit та push

### 34. base_api
- [ ] Аналіз структури модуля
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення API endpoints
- [ ] Заміна `type='json'` на `type='jsonrpc'`
- [ ] Тестування API
- [ ] Git commit та push

---

## 📋 Фаза 3: Висока складність

### 35. mobius_portal_aklima
- [ ] Повний аналіз модуля
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення Python controllers
- [ ] Оновлення portal templates
- [ ] Оновлення JavaScript/OWL
- [ ] Оновлення SCSS/CSS
- [ ] Комплексне тестування
- [ ] Git commit та push

### 36. mobius_registration_aklima
- [ ] Повний аналіз модуля
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення registration flow
- [ ] Оновлення templates
- [ ] Оновлення JavaScript
- [ ] Тестування реєстрації
- [ ] Git commit та push

### 37. openapi
- [ ] Аналіз OCA версії для v18
- [ ] Порівняння з поточним кодом
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення API specification
- [ ] Оновлення endpoints
- [ ] Тестування всіх endpoints
- [ ] Git commit та push

### 38. base_account_budget
- [ ] Аналіз OCA версії для v18
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення Python моделей
- [ ] Перевірка account змін
- [ ] Оновлення views
- [ ] Тестування бюджетів
- [ ] Git commit та push

### 39. account_dynamic_reports
- [ ] Аналіз структури звітів
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення report моделей
- [ ] Оновлення _read_group() викликів
- [ ] Оновлення templates
- [ ] Комплексне тестування звітів
- [ ] Git commit та push

### 40. l10n_ua
- [ ] Перевірка офіційної версії OCA/l10n-ukraine
- [ ] Аналіз змін chart of accounts
- [ ] Оновлення `__manifest__.py`
- [ ] Оновлення tax templates
- [ ] Оновлення data files
- [ ] Тестування локалізації
- [ ] Git commit та push

---

## ✅ Завершальні кроки

- [ ] Оновлення `odoo18.conf` з шляхом до custom_addons
- [ ] Встановлення всіх модулів разом
- [ ] Тестування взаємодії модулів
- [ ] Фінальний push всіх змін
- [ ] Merge в main гілку
- [ ] Деплой на production

---

## 📝 Нотатки

### Виявлені проблеми
_(Записувати проблеми під час міграції)_

1. 

### Рішення
_(Записувати знайдені рішення)_

1. 

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

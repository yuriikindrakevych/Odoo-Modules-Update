## 1. Розділ "Дати блокування", не відкривається. Помилка:
   RPC_ERROR

404: Not Found

Occured on odoo-upgrade.echo-digital.es on model account.lock.date on 2025-12-22 14:12:24 GMT

Traceback (most recent call last):
File "/www/wwwroot/odoo18-migration/odoo/addons/web/controllers/dataset.py", line 22, in _call_kw_readonly
model_class = request.registry[params['model']]
~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
File "/www/wwwroot/odoo18-migration/odoo/odoo/modules/registry.py", line 244, in __getitem__
return self.models[model_name]
~~~~~~~~~~~^^^^^^^^^^^^
KeyError: 'account.lock.date'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
File "/www/wwwroot/odoo18-migration/odoo/odoo/http.py", line 2576, in __call__
response = request._serve_db()
^^^^^^^^^^^^^^^^^^^
File "/www/wwwroot/odoo18-migration/odoo/odoo/http.py", line 2102, in _serve_db
readonly = readonly(rule.endpoint.func.__self__)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/www/wwwroot/odoo18-migration/odoo/addons/web/controllers/dataset.py", line 24, in _call_kw_readonly
raise NotFound() from e
werkzeug.exceptions.NotFound: 404 Not Found: The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.

The above server error caused the following client error:
OwlError: An error occured in the owl lifecycle (see this Error's "cause" property)
Error: An error occured in the owl lifecycle (see this Error's "cause" property)
at handleError (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:972:101)
at App.handleError (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:1630:29)
at ComponentNode.initiateRender (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:1064:19)

Caused by: RPC_ERROR: 404: Not Found
RPC_ERROR
at makeErrorFromResponse (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:3165:165)
at XMLHttpRequest.<anonymous> (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:3170:13)



########## 2. Розділ "Google таблиці", не відкривається. Помилка:
UncaughtPromiseError

Uncaught Promise > View types not defined tree found in act_window action 795

Occured on odoo-upgrade.echo-digital.es on 2025-12-22 14:16:20 GMT

Error: View types not defined tree found in act_window action 795
    at _executeActWindowAction (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:10085:26)
    at Object.doAction (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:10110:8)
    at async Object.selectMenu (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:10309:1)

############ 3. Розділ "Budgets", не відкривається. Помилка:
RPC_ERROR

404: Not Found

Occured on odoo-upgrade.echo-digital.es on model budget.budget on 2025-12-22 14:17:46 GMT

Traceback (most recent call last):
  File "/www/wwwroot/odoo18-migration/odoo/addons/web/controllers/dataset.py", line 22, in _call_kw_readonly
    model_class = request.registry[params['model']]
                  ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "/www/wwwroot/odoo18-migration/odoo/odoo/modules/registry.py", line 244, in __getitem__
    return self.models[model_name]
           ~~~~~~~~~~~^^^^^^^^^^^^
KeyError: 'budget.budget'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/www/wwwroot/odoo18-migration/odoo/odoo/http.py", line 2576, in __call__
    response = request._serve_db()
               ^^^^^^^^^^^^^^^^^^^
  File "/www/wwwroot/odoo18-migration/odoo/odoo/http.py", line 2102, in _serve_db
    readonly = readonly(rule.endpoint.func.__self__)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/www/wwwroot/odoo18-migration/odoo/addons/web/controllers/dataset.py", line 24, in _call_kw_readonly
    raise NotFound() from e
werkzeug.exceptions.NotFound: 404 Not Found: The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.

The above server error caused the following client error:
OwlError: An error occured in the owl lifecycle (see this Error's "cause" property)
    Error: An error occured in the owl lifecycle (see this Error's "cause" property)
        at handleError (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:972:101)
        at App.handleError (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:1630:29)
        at ComponentNode.initiateRender (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:1064:19)

Caused by: RPC_ERROR: 404: Not Found
    RPC_ERROR
        at makeErrorFromResponse (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:3165:165)
        at XMLHttpRequest.<anonymous> (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:3170:13)

########### 4. Розділ "Активи", не відкривається. Помилка:
RPC_ERROR

404: Not Found

Occured on odoo-upgrade.echo-digital.es on model account.asset.asset on 2025-12-22 14:19:13 GMT

Traceback (most recent call last):
  File "/www/wwwroot/odoo18-migration/odoo/addons/web/controllers/dataset.py", line 22, in _call_kw_readonly
    model_class = request.registry[params['model']]
                  ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "/www/wwwroot/odoo18-migration/odoo/odoo/modules/registry.py", line 244, in __getitem__
    return self.models[model_name]
           ~~~~~~~~~~~^^^^^^^^^^^^
KeyError: 'account.asset.asset'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/www/wwwroot/odoo18-migration/odoo/odoo/http.py", line 2576, in __call__
    response = request._serve_db()
               ^^^^^^^^^^^^^^^^^^^
  File "/www/wwwroot/odoo18-migration/odoo/odoo/http.py", line 2102, in _serve_db
    readonly = readonly(rule.endpoint.func.__self__)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/www/wwwroot/odoo18-migration/odoo/addons/web/controllers/dataset.py", line 24, in _call_kw_readonly
    raise NotFound() from e
werkzeug.exceptions.NotFound: 404 Not Found: The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.

The above server error caused the following client error:
OwlError: An error occured in the owl lifecycle (see this Error's "cause" property)
    Error: An error occured in the owl lifecycle (see this Error's "cause" property)
        at handleError (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:972:101)
        at App.handleError (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:1630:29)
        at ComponentNode.initiateRender (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:1064:19)

Caused by: RPC_ERROR: 404: Not Found
    RPC_ERROR
        at makeErrorFromResponse (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:3165:165)
        at XMLHttpRequest.<anonymous> (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:3170:13)



########### 5. Розділ "Активи", не відкривається. Помилка:
RPC_ERROR

404: Not Found

Occured on odoo-upgrade.echo-digital.es on model account.asset.asset on 2025-12-22 14:19:13 GMT

Traceback (most recent call last):
  File "/www/wwwroot/odoo18-migration/odoo/addons/web/controllers/dataset.py", line 22, in _call_kw_readonly
    model_class = request.registry[params['model']]
                  ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "/www/wwwroot/odoo18-migration/odoo/odoo/modules/registry.py", line 244, in __getitem__
    return self.models[model_name]
           ~~~~~~~~~~~^^^^^^^^^^^^
KeyError: 'account.asset.asset'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/www/wwwroot/odoo18-migration/odoo/odoo/http.py", line 2576, in __call__
    response = request._serve_db()
               ^^^^^^^^^^^^^^^^^^^
  File "/www/wwwroot/odoo18-migration/odoo/odoo/http.py", line 2102, in _serve_db
    readonly = readonly(rule.endpoint.func.__self__)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/www/wwwroot/odoo18-migration/odoo/addons/web/controllers/dataset.py", line 24, in _call_kw_readonly
    raise NotFound() from e
werkzeug.exceptions.NotFound: 404 Not Found: The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.

The above server error caused the following client error:
OwlError: An error occured in the owl lifecycle (see this Error's "cause" property)
    Error: An error occured in the owl lifecycle (see this Error's "cause" property)
        at handleError (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:972:101)
        at App.handleError (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:1630:29)
        at ComponentNode.initiateRender (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:1064:19)

Caused by: RPC_ERROR: 404: Not Found
    RPC_ERROR
        at makeErrorFromResponse (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:3165:165)
        at XMLHttpRequest.<anonymous> (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:3170:13)



########### 6. Розділ "Ремонти", не відкривається. Помилка:
RPC_ERROR

404: Not Found

Occured on odoo-upgrade.echo-digital.es on model repair.order on 2025-12-22 14:35:07 GMT

Traceback (most recent call last):
  File "/www/wwwroot/odoo18-migration/odoo/addons/web/controllers/dataset.py", line 22, in _call_kw_readonly
    model_class = request.registry[params['model']]
                  ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "/www/wwwroot/odoo18-migration/odoo/odoo/modules/registry.py", line 244, in __getitem__
    return self.models[model_name]
           ~~~~~~~~~~~^^^^^^^^^^^^
KeyError: 'repair.order'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/www/wwwroot/odoo18-migration/odoo/odoo/http.py", line 2576, in __call__
    response = request._serve_db()
               ^^^^^^^^^^^^^^^^^^^
  File "/www/wwwroot/odoo18-migration/odoo/odoo/http.py", line 2102, in _serve_db
    readonly = readonly(rule.endpoint.func.__self__)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/www/wwwroot/odoo18-migration/odoo/addons/web/controllers/dataset.py", line 24, in _call_kw_readonly
    raise NotFound() from e
werkzeug.exceptions.NotFound: 404 Not Found: The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.

The above server error caused the following client error:
OwlError: An error occured in the owl lifecycle (see this Error's "cause" property)
    Error: An error occured in the owl lifecycle (see this Error's "cause" property)
        at handleError (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:972:101)
        at App.handleError (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:1630:29)
        at ComponentNode.initiateRender (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:1064:19)

Caused by: RPC_ERROR: 404: Not Found
    RPC_ERROR
        at makeErrorFromResponse (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:3165:165)
        at XMLHttpRequest.<anonymous> (https://odoo-upgrade.echo-digital.es/web/assets/7bdbc3d/web.assets_web.min.js:3170:13)


########### 7. Розділ "Продажі" - при відкритті документа sale.order помилка "due_amount field is undefined"

**Помилка:**
```
UncaughtPromiseError > OwlError
Caused by: Error: "sale.order"."due_amount" field is undefined.
    at Field.parseFieldNode
```

**Причина:**
Модуль `base_accounting_kit` використовував застарілий синтаксис `attrs=` в XML views та поле `due_amount` не було явно підвантажене у view.

**Виправлення (файл `base_accounting_kit/views/credit_limit_view.xml`):**
1. Замінено синтаксис `attrs="{'invisible':[...]}"` на новий формат Odoo 17+: `invisible="expression"`
2. Додано приховане поле `<field name="due_amount" invisible="1"/>` для забезпечення завантаження поля у клієнтську частину OWL
3. Оновлено умови invisible з формату `attrs="{'invisible':['|',('field1','=',False),('field2','not in',...)]}"` на формат `invisible="not field1 or field2 not in (...)"`

**Статус:** ВИПРАВЛЕНО
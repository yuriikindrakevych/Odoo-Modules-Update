# -*- coding: utf-8 -*-
{
    "name": "Mobius Inventory Supplier",
    "description": "Inventory Supplier (sync with 1C Aclima)",
    "author": "Mobius team",
    "version": "18.0.1.0.0",
    "installable": True,
    "application": False,
    # any module necessary for this one to work correctly
    "depends": ["base", "stock", "sale"],
    # always loaded
    "assets": {
       "web.assets_backend": [
           "mobius_inventory_supplier/static/src/js/run_synchronisation_action_tree.js",
           "mobius_inventory_supplier/static/src/xml/run_synchronisation_button_tree.xml",
           "mobius_inventory_supplier/static/src/xml/sale_stock.xml",
       ],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/inventory_supplier_view.xml",
        "views/menuitem_inventory_reporting_supplier.xml",
        "views/scheduler_inventory_supplier_sync.xml",
        "views/res_config_settings_views.xml",
        "views/sale_order_views.xml",
    ],
    "license": "Other proprietary",
}

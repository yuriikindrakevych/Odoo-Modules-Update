odoo.define("run_synchronisation_action.tree_button", function (require) {
    "use strict";
    var rpc = require("web.rpc");
    var ListController = require("web.ListController");
    var ListView = require("web.ListView");
    var viewRegistry = require("web.view_registry");
    var TreeButton = ListController.extend({
        buttons_template: "run_synchronisation_action.buttons",
        events: _.extend({}, ListController.prototype.events, {
            "click .run_synchronisation_action_tree": "_RunSync",
        }),
        _RunSync: function () {
            return rpc.query({
                model: "inventory.supplier",
                method: "inventory_supplier_sync_manual",
                args: [""],
            })
        }
    });
    var InventorySupplierListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: TreeButton,
        }),
    });
    viewRegistry.add("run_synchronisation_action_tree", InventorySupplierListView);
});

odoo.define("open_wizard_contact_by_vat.tree_button", function (require) {
    "use strict";
    var _t = require("web.core")._t;
    var ListController = require("web.ListController");
    var ListView = require("web.ListView");
    var viewRegistry = require("web.view_registry");
    var TreeButton = ListController.extend({
        buttons_template: "open_wizard_contact_by_vat.buttons",
        events: _.extend({}, ListController.prototype.events, {
            "click .open_wizard_contact_by_vat_action_tree": "_OpenWizardList",
        }),
        _OpenWizardList: function () {
            var self = this;
            this.do_action({
                type: "ir.actions.act_window",
                res_model: "contact_by_vat.wizard",
                name: _t("Creating of Contact by the VAT code"),
                view_mode: "form",
                view_type: "form",
                views: [[false, "form"]],
                target: "new",
                res_id: false,
            });
        }
    });
    var ResPartnerListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: TreeButton,
        }),
    });
    viewRegistry.add("open_wizard_contact_by_vat_tree", ResPartnerListView);
});
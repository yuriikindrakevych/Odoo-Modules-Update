odoo.define("open_wizard_contact_by_vat.kanban_button", function(require) {
   "use strict";
   var _t = require("web.core")._t;
   var KanbanController = require("web.KanbanController");
   var KanbanView = require("web.KanbanView");
   var viewRegistry = require("web.view_registry");
   var KanbanButton = KanbanController.include({
       buttons_template: "open_wizard_contact_by_vat.button",
       events: _.extend({}, KanbanController.prototype.events, {
           "click .open_wizard_contact_by_vat_action_kanban": "_OpenWizardKanban",
       }),
       _OpenWizardKanban: function () {
       var self = this;
        this.do_action({
           type: "ir.actions.act_window",
           res_model: "contact_by_vat.wizard",
           name : _t("Creating of Contact by the VAT code"),
           view_mode: "form",
           view_type: "form",
           views: [[false, "form"]],
           target: "new",
           res_id: false,
       });
   }
   });
   var PartnerKanbanView = KanbanView.extend({
       config: _.extend({}, KanbanView.prototype.config, {
           Controller: KanbanButton
       }),
   });
   viewRegistry.add("button_in_kanban", PartnerKanbanView);
});
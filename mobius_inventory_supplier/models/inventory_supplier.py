from odoo import models, fields, api, tools, exceptions, _
from . import product_inventory_api, product_template_supplier


class InventorySupplier(models.Model):
    # Information about products and suppliers related to data from the API
    _name = "inventory.supplier"
    _description = "Inventory Supplier (sync with 1C Aclima)"
    _inherit = ["product.template.supplierinfo", "product.inventory.api"]
    _auto = True

    # _sql_constraints = [
    #     ("inventory_supplier_inventory_code_uniq", "unique(inventory_code)", "Inventory code must be unique!"),
    # ]

    def init(self):
        self.refresh_information()

    def refresh_information(self):
        # truncate inventory_supplier (delete all records)
        record_set = self.search([])
        record_set.unlink()

        sql_query = """select
                   p.id as product_tmpl_id,
                   p.default_code, p.name, p.category_name, p.supplier_code, p.supplier_name, p.vendor_name,
                   a.inventory, a.inventory_code, a.inventory_description, a.inventory_article, a.inventory_quantity,
                   a.purchaseorders_income
              from product_template_supplierinfo p
              full join product_inventory_api a on (p.supplier_code = a.inventory_code and a.inventory_code is not null)
        """
        self._cr.execute(sql_query)

        vals = self._cr.dictfetchall()
        if vals:
            self.env["inventory.supplier"].create(vals)

    def warning_and_redirect_to_settings(self, param_subname: str):
        msg = _("Parameter <Aclima API %s> is absent in General Settings (Integrations). Please, set it up.") % param_subname
        action = self.env.ref("product.product_template_kanban_view")  # base.res_config_settings_view_form
        raise exceptions.RedirectWarning(msg, action.id, _("Go to Settings"))

    def validation_warning(self, param_subname: str):
        msg = _("Parameter <Aclima API %s> is absent in General Settings (Integrations). Please, set it up.") % param_subname
        raise exceptions.ValidationError(msg)

    def inventory_supplier_sync(self):
        # DB views refresh automatically and cannot be updated manualy! (product_template_supplierinfo)
        if self.refresh_information_api():
            # if refresh_information_api (sync with API) successful, then run refresh_information
            self.refresh_information()

    def inventory_supplier_sync_manual(self):
        # check parameters in settings
        if not self.env["ir.config_parameter"].sudo().get_param("aclima_API_URL"):
            self.validation_warning("URL")
        if not self.env["ir.config_parameter"].sudo().get_param("aclima_API_login"):
            self.validation_warning("login")
        if not self.env["ir.config_parameter"].sudo().get_param("aclima_API_password"):
            self.validation_warning("password")

        # Run synchronisation with API manual with refresh page
        self.inventory_supplier_sync()
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

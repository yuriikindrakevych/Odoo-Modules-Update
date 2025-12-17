from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    phone_for_search = fields.Char(
        compute="_compute_phone_for_search",
        store=True, )

    @api.depends("phone")
    def _compute_phone_for_search(self):
        for obj in self:
            if obj.phone:
                phone_for_search = obj.phone
                for symbols in ["+", "(", ")", "-", " "]:
                    phone_for_search = phone_for_search.replace(symbols, "")
                obj.phone_for_search = phone_for_search
            else:
                obj.phone_for_search = False

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo import _


class ResBank(models.Model):
    _inherit = "res.bank"

    city_ua = fields.Many2one(
        comodel_name="mobius_catalogue_koatuu.settlement", string="Settlement",
        domain="[('res_country_state_id', '=?', state)]"
    )

    @api.onchange("city_ua")
    def _onchange_city(self):
        if (self.city_ua and not self.state):
            raise ValidationError(_("First choose the state!"))
        else:
            self.city = self.city_ua.name

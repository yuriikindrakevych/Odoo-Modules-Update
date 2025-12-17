from odoo import fields, models


class Settlement(models.Model):
    _name = "mobius_catalogue_koatuu.settlement"
    _description = "Settlement"
    _order = "name"

    country_id = fields.Many2one(
        comodel_name="res.country", required=True
    )
    res_country_state_id = fields.Many2one(
        comodel_name="res.country.state", string="State", required=True
    )
    settlement_type_id = fields.Many2one(
        comodel_name="mobius_catalogue_koatuu.settlement_type", string="Type", required=True
    )
    name = fields.Char(required=True)

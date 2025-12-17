from odoo import fields, models


class SettlementType(models.Model):
    _name = "mobius_catalogue_koatuu.settlement_type"
    _description = "Settlement type"

    category = fields.Char(required=True)
    name = fields.Text(required=True)

    _sql_constraints = [
        ("settlemet_type_category_uniq", "unique(category)", "Category must be unique!"),
        ("settlemet_type_name_uniq",     "unique(name)",     "Name must be unique!"),
    ]

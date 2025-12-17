from odoo import fields, models, api, _


class Partner(models.Model):
    _inherit = "res.partner"

    ensurance = fields.Boolean("Ensurance")
from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    stage_id = fields.Many2one("contact.stage")

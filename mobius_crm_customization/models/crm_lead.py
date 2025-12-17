from odoo import models, fields


class Lead(models.Model):
    _inherit = "crm.lead"

    linkedin = fields.Char()
    linkedin_company = fields.Char()

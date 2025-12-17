from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    linkedin = fields.Char(string="LinkedIn")
    linkedin_company = fields.Char(string="LinkedIn Company")

# -*- coding: utf-8 -*-
from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    contact_autofill_team_ids = fields.Many2many(
        comodel_name='crm.team',
        relation='res_company_crm_team_autofill_rel',
        column1='company_id',
        column2='team_id',
        string='Sales Teams to Autofill Based on Contact'
    )

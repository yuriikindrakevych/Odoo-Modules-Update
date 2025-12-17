#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class Users(models.Model):
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        users = super(Users, self).create(vals_list)
        company = self.env["res.company"].browse(self.env.context['allowed_company_ids'][0])
        if not company:
            return users
        for user in users:
            if user.has_group('base.group_portal'):
                pricelist = company.partner_id.property_product_pricelist
                if pricelist:
                    user.partner_id.property_product_pricelist = pricelist
        return users


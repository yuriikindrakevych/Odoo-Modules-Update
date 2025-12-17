#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    profile_id = fields.Many2one("profile.res.partner.bank", "Profile")

    def action_add_select_to_profile(self):
        bank_ids = self.browse(self.env.context.get("active_ids"))
        profile_id = self.env["profile.res.partner.bank"].browse(self.env.context.get("profile_id"))
        for rec in bank_ids:
            if not rec.profile_id:
                rec.profile_id = profile_id


class ProfileResPartnerBank(models.Model):
    _name = "profile.res.partner.bank"

    name = fields.Char("Name")
    description = fields.Char("Description")
    currency_id = fields.Many2one("res.currency", string="Currency")
    bank_ids = fields.One2many("res.partner.bank", "profile_id", string="Banks")

    def button_show_banks(self):
        xmlid = "mobius_sale_order_reports.action_bank_form_show_bank"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        action["domain"] = [("id", "in", self.bank_ids.ids)]
        return action

    def button_add_banks(self):
        xmlid = "mobius_sale_order_reports.action_bank_form_add_banks"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        action["target"] = "new"
        action["context"] = {
        "profile_id" : self.id,
        }
        action["domain"] = [("profile_id", "=", False), ("currency_id", "=", self.env.context.get("currency_id"))]
        return action

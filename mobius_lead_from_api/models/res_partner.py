#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo import _

class ResPartner(models.Model):
    _inherit = "res.partner"

    company_type = fields.Selection(string="Company Type",
        selection=[("person", "Individual"), ("company", "Company")],
        compute="_compute_company_type", inverse="_write_company_type", store=True)
    right_services_ids = fields.One2many("rights.of.external.services", "partner_id", "Services Rights")
    techinal_password = fields.Char(store=True)
    has_user = fields.Boolean(help="Technical field", compute="_compute_has_user")
    linkedin = fields.Char(string="LinkedIn")
    linkedin_company = fields.Char(string="LinkedIn Company")

    def _compute_has_user(self):
        for contact in self:
            search_some_user = self.env["res.users"].search([("partner_id", "=", contact.id)], limit=1)
            if search_some_user:
                contact.has_user = True
            else:
                contact.has_user = False

    def create_user(self):
        search_some_user = self.env["res.users"].search([("partner_id", "=", self.id)], limit=1)
        if search_some_user:
            raise ValidationError(_("This contact already has a user"))
        if not self.name:
            raise ValidationError(_("Contact dont have name"))
        if not self.email:
            raise ValidationError(_("Be sure to specify an email"))
        code_ok = True
        new_code = None
        while code_ok:
            new_code = self.env["code.generation"]._create_code()
            search_code = self.env["res.users"].search([("access_code_to_external_systems", "=", new_code)])
            if search_code:
                continue
            else:
                break
        techinal_password = self.env["code.generation"]._create_random_string_upper_and_lower()
        self.write({
            "techinal_password": techinal_password,
            })
        user = self.env["res.users"].with_context(no_reset_password=True).sudo().create({
            "name": self.name,
            "login": self.email,
            "partner_id": self.id,
            "sel_groups_1_9_10": "9",
            "access_code_to_external_systems" : new_code,
        })
        user.sudo().write({
            "password": techinal_password,
            })
        notification = {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("OK"),
                "message": _("User has been created."),
                "type": "success",
                "sticky": False,
            },
        }
        self.has_user = True
        return notification

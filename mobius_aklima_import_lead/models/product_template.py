#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
import csv
import time
from odoo.modules.module import get_module_resource
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def mobius_import_lead_check_vat(self, vat):
        check_lead = self.env["crm.lead"].search([("vat", "=", vat)], limit=1)
        if check_lead:
            return False
        check_contact = self.env["res.partner"].search([("vat", "=", vat)], limit=1)
        if check_contact:
            return False
        return True

    def mobius_import_lead_check_email(self, email):
        check_lead = self.env["crm.lead"].search([("email_from", "=", email)], limit=1)
        if check_lead:
            return False
        check_lead = self.env["crm.lead"].search([("email_cc", "=", email)], limit=1)
        if check_lead:
            return False

        check_contact = self.env["res.partner"].search([("email", "=", email)], limit=1)
        if check_contact:
            return False
        return True

    def mobius_import_lead_check_phone(self, phone):
        check_lead = self.env["crm.lead"].search([("phone", "=", phone)], limit=1)
        if check_lead:
            return False
        check_lead = self.env["crm.lead"].search([("mobile", "=", phone)], limit=1)
        if check_lead:
            return False

        check_contact = self.env["res.partner"].search([("phone", "=", phone)], limit=1)
        if check_contact:
            return False
        check_contact = self.env["res.partner"].search([("mobile", "=", phone)], limit=1)
        if check_contact:
            return False
        return True

    def mobius_import_lead(self):
        #path = get_module_resource("mobius_test", "models/replace_loc_sequence.csv")
        with open(get_module_resource('mobius_aklima_import_lead', 'models', 'baza2.csv'), 'r') as file:
            reader = csv.reader(file, delimiter=',')
            first = 0
            for row in reader:
                if first == 0:
                    first += 1
                    continue
                vat = str(row[2]).strip()
                if vat != "0":
                    if not self.mobius_import_lead_check_vat(vat):
                        _logger.info("SKIP IMPORT (vat) ID=%s", int(row[0]))
                        continue

                email = str(row[9]).strip()
                if email != "0":
                    if not self.mobius_import_lead_check_email(email):
                        _logger.info("SKIP IMPORT (email) ID=%s", int(row[0]))
                        continue

                phone = str(row[8]).strip()
                if phone != "0":
                    if not self.mobius_import_lead_check_phone(phone):
                        _logger.info("SKIP IMPORT (phone) ID=%s", int(row[0]))
                        continue

                try:
                    region = str(row[3]).strip()
                    oblast = self.env["res.country.state"].search([("name", "=", region)])
                    self.env["crm.lead"].create({
                        "name": str(row[1]).strip(),
                        "vat": vat,
                        "state_id": oblast.id if oblast else False,
                        "street": str(row[4]).strip(),
                        "zip": str(row[5]).strip(),
                        "city": str(row[6]).strip(),
                        "contact_name": str(row[7]).strip(),
                        "phone": phone,
                        "email_from": email,
                        "function": str(row[10]).strip(),
                        "source_id": 61,
                    })
                except Exception as err:
                    _logger.error('Creation error: %s' % (str(err)))
                    _logger.error("ID=%s", int(row[0]))

# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Lead(models.Model):
    _inherit = "crm.lead"

    def get_by_phones(self, phone):
        with_contact = self.env.context.get("with_contact") or False
        return self.with_context({"with_contact": with_contact, "only_first": True}).all_by_phones(phone)

    def all_by_phones(self, phone):
        with_contact = self.env.context.get("with_contact") or False
        only_first = self.env.context.get("only_first") or False
        objects = []
        common = self.env["phone.common"]
        leads = self.search([("partner_id", "!=", False)], order="id") if with_contact else self.search([], order="id")
        for item in leads:
            found = False
            if item.phone:
                found = common.compare_phone_numbers(phone, item.phone)
            if not found and item.mobile:
                found = common.compare_phone_numbers(phone, item.mobile)
            if found:
                if only_first:
                    return item
                else:
                    objects.append(item)
        # _logger.info(f"all_by_phones -> ids={ids}")
        # objects = self.search(["id", "in", ids], order="id")
        # _logger.info(f"all_by_phones -> objects={objects}")
        return None if only_first else objects

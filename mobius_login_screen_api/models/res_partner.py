# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = "res.partner"

    def get_by_phones(self, phone):
        _logger.info(f"get_by_phones -> context={self.env.context}")
        with_user = self.env.context.get("with_user") or False
        has_group = self.env.context.get("has_group") or None
        return self.with_context({"with_user": with_user, "has_group": has_group, "only_first": True}).all_by_phones(phone)

    def all_by_phones(self, phone):
        _logger.info(f"all_by_phones -> context={self.env.context}")
        with_user = self.env.context.get("with_user") or False
        has_group = self.env.context.get("has_group") or None
        only_first = self.env.context.get("only_first") or False
        _logger.info(f"all_by_phones -> phone={phone}, with_user={with_user}, has_group={has_group}, only_first={only_first}")

        objects = []
        common = self.env["phone.common"]
        for item in self.search([], order="id"):
            found = False
            if item.phone:
                found = common.compare_phone_numbers(phone, item.phone)
            if not found and item.mobile:
                found = common.compare_phone_numbers(phone, item.mobile)
            if found:
                # _logger.info(f"all_by_phones -> partner={item}, partner.name={item.name}")
                # _logger.info(f"all_by_phones -> item.phone={item.phone}, item.mobile={item.mobile}")
                if with_user:
                    user_domain = [
                        ("partner_id", "=", item.id),
                    ]
                    user_id_from_partner = self.env["res.users"].search(user_domain, limit=1)
                    # _logger.info(f"all_by_phones -> user_id_from_partner={user_id_from_partner}")
                    if user_id_from_partner:
                        if has_group and not user_id_from_partner.has_group(has_group):
                            continue
                    else:
                        continue

                if only_first:
                    return item
                else:
                    objects.append(item)
        # _logger.info(f"all_by_phones -> ids={ids}")
        # objects = self.search(["id", "in", ids], order="id")
        # _logger.info(f"all_by_phones -> objects={objects}")
        return None if only_first else objects

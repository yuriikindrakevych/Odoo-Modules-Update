# -*- coding: utf-8 -*-
from odoo import api, models, tools

import logging
_logger = logging.getLogger(__name__)

class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def message_route(self, message, message_dict, model=None, thread_id=None, custom_values=None):
        try:
            _logger.debug("message=%s, message_gict=%s, model=%s, thread_id=%s, custom_values=%s", str(message), str(message_dict), str(model), str(thread_id), str(custom_values))
            ret = super().message_route(message, message_dict, model, thread_id, custom_values)
            _logger.debug("message_route ret=%s", str(ret))
            return ret
        except ValueError as e:
            _logger.error("error: %s", str(e))
            if "No possible route" in str(e):
                ret = self._route_by_email(message, message_dict, model, thread_id, custom_values)
                _logger.debug("_route_by_email ret=%s", str(ret))
                if ret:
                    return ret
            raise

    def _route_by_email(self, message, message_dict, model, thread_id, custom_values):
        email_to = message_dict["to"]
        users = []
        for email in tools.email_split(email_to):
            _logger.debug("Email check: %s", email)
            criteria = [
                "|",
                "|",
                "|",
                ("login",         "=", email),
                ("email",         "=", email),
                ("work_email",    "=", email),
                ("private_email", "=", email)
            ]
            match_users = self.env["res.users"].sudo().search(criteria)
            _logger.debug("email_to=%s, users=%s", email_to, match_users)
            users += match_users

        if not users:
            _logger.debug("Searching for admin")
            adm_partner = self.env.ref("base.partner_admin")
            _logger.debug("adm_partner=%s", str(adm_partner))
            adm_users = adm_partner.user_ids
            _logger.debug("adm_users=%s", str(adm_users))
            if adm_users:
                users.append(adm_users[0])

        return [("res.users", thread_id or user.id, custom_values, user.id, None) for user in users]

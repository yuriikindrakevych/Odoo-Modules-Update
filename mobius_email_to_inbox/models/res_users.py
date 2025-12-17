# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.tools import pycompat

class ResUsers(models.Model):
    _inherit = "res.users"

    def _message_post_get_pid(self):
        self.ensure_one()
        if "thread_model" in self.env.context:
            self = self.with_context(thread_model="res.users")
        return self.partner_id.id

    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, **kwargs):
        self.ensure_one()
        current_pids = []
        partner_ids = kwargs.get("partner_ids", [])
        user_pid = self._message_post_get_pid()
        for partner_id in partner_ids:
            if isinstance(partner_id, (list, tuple)) and (partner_id[0] == 4) and (len(partner_id) == 2):
                current_pids.append(partner_id[1])
            elif isinstance(partner_id, (list, tuple)) and (partner_id[0] == 6) and (len(partner_id) == 3):
                current_pids.append(partner_id[2])
            elif isinstance(partner_id, pycompat.integer_types):
                current_pids.append(partner_id)
        if user_pid not in current_pids:
            partner_ids.append(user_pid)
        kwargs["partner_ids"] = partner_ids

        # Older versions
        #return self.env["mail.thread"].message_post(**kwargs)
        # V. 15+
        return self.env["mail.thread"].message_notify(**kwargs)

    def message_update(self, msg_dict, update_vals=None):
        return True

    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None, force=True):
        return True

    def message_partner_info_from_emails(self, emails, link_mail=False):
        return self.env["mail.thread"].message_partner_info_from_emails(emails, link_mail=link_mail)

    def message_get_suggested_recipients(self):
        return dict((res_id, []) for res_id in self._ids)

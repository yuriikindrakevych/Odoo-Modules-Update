# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = "account.move"

    def _check_balanced(self, container=None):
        # Odoo 18: _check_balanced now accepts container parameter and returns context manager
        check_balanced_skip = self.env["ir.config_parameter"].sudo().get_param("account_move_check_balanced_skip")
        if check_balanced_skip:
            # Return a dummy context manager that does nothing
            from contextlib import nullcontext
            return nullcontext()
        else:
            if container is not None:
                return super(AccountMove, self)._check_balanced(container)
            return super(AccountMove, self)._check_balanced()

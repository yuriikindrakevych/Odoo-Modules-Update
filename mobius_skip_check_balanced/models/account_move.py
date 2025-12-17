# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = "account.move"

    def _check_balanced(self):
        check_balanced_skip = self.env["ir.config_parameter"].sudo().get_param("account_move_check_balanced_skip")
        if check_balanced_skip:
            return True
        else:
            return super(AccountMove, self)._check_balanced()

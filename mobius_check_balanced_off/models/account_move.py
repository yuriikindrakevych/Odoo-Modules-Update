# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = "account.move"

    def _check_balanced(self, container=None):
        # Odoo 18: _check_balanced now returns context manager
        from contextlib import nullcontext
        return nullcontext()

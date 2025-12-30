# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
"""
Odoo 18 compatibility: This module recreates the account.common.report model
that was removed in Odoo 17+. It provides base functionality for accounting
report wizards.
"""

from odoo import api, fields, models


class AccountCommonReport(models.TransientModel):
    _name = 'account.common.report'
    _description = 'Account Common Report'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    journal_ids = fields.Many2many(
        'account.journal',
        string='Journals',
        required=True,
        default=lambda self: self.env['account.journal'].search([
            ('company_id', '=', self.env.company.id)
        ])
    )
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    target_move = fields.Selection(
        [('posted', 'All Posted Entries'),
         ('all', 'All Entries')],
        string='Target Moves',
        required=True,
        default='posted'
    )

    def _build_contexts(self, data):
        """Build context for report generation."""
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        result['date_from'] = data['form']['date_from'] or False
        result['date_to'] = data['form']['date_to'] or False
        result['strict_range'] = True if result['date_from'] else False
        result['company_id'] = data['form']['company_id'][0] if data['form'].get('company_id') else self.env.company.id
        return result

    def _print_report(self, data):
        """Override this method in child classes to generate specific reports."""
        raise NotImplementedError()

    def check_report(self):
        """Validate and generate the report."""
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read([
            'date_from', 'date_to', 'journal_ids', 'target_move', 'company_id'
        ])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
        return self.with_context(discard_logo_check=True)._print_report(data)

    def pre_print_report(self, data):
        """Hook method for pre-processing report data."""
        return data

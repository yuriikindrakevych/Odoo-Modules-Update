#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)


import inspect
import traceback

class Meeting(models.Model):
    _inherit = "calendar.event"

    activity_id_test = fields.Integer("Activity ID")

    def _get_default_activity_type_id_real(self):
        activity_type = self.env["mail.activity.type"].search([("category", "=", "meeting")], limit=1)
        if activity_type:
            return activity_type.id
        return False

    activity_type_id_real = fields.Many2one("mail.activity.type", string="Activity Type", default=_get_default_activity_type_id_real)
    activity_type_id_boolean = fields.Boolean(default=False)
    


    activity_type_id = fields.Many2one("mail.activity.type", string="Activity Compute",
        compute="_compute_activity_type_id", inverse="_inverse_activity_type_id")
    activity_type_id_name = fields.Char(related="activity_type_id.name")

    def _inverse_activity_type_id(self):
        pass


    @api.onchange("activity_type_id_real")
    def onchange_activity_type_id_real(self):
        self.write({"activity_type_id_boolean": True})

    def _compute_activity_type_id(self):
        for rec in self:
            if rec.activity_type_id_boolean:
                rec.activity_type_id = rec.activity_type_id_real.id
                continue

            elif rec.activity_ids:
                activity = rec.activity_ids[0]
                rec.activity_type_id = activity.activity_type_id.id
                rec.activity_type_id_real = activity.activity_type_id.id
                rec.activity_type_id_boolean = True
                continue

            elif not rec.activity_ids and not rec.activity_type_id_boolean:
                 rec.activity_type_id = rec.activity_type_id_real.id
                 continue
                 
            rec.activity_type_id = False     

    def get_activity_type_id_char(self):
        return self.activity_type_id.name

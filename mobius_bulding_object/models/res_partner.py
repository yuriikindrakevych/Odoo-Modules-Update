#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo import _

import logging
import inspect
import traceback
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    building_object_item_count = fields.Integer(
        string="Building Object count",
        compute="_compute_building_object_item_count")

    def method_traceback(self):
        frame = inspect.currentframe()
        stack_trace = traceback.format_stack(frame)
        _logger.info(''.join(stack_trace))


    # def write(self, vals):
    #     _logger.info("self=%s, vals=%s", self, vals)
    #     self.method_traceback()
    #
    #     res = super().write(vals)

    def _get_building_object_domain(self):
        domain = [
            ("state", "!=", "cancel"),
            "|",
            "|",
            "|",
            "|",
            ("partner_id", "=", self.id),
            ("investor_id", "=", self.id),
            ("designer_id", "=", self.id),
            ("general_executor_id", "=", self.id),
            ("installer_id", "=", self.id)
        ]

        return domain

    def _compute_building_object_item_count(self):
        building_object = self.env["building.object"]
        for rec in self:
            domain = rec._get_building_object_domain()
            rec.building_object_item_count = building_object.search_count(domain)

    def open_building_object(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mobius_bulding_object.action_building_object_open")

        action["context"] = {"search_default_my_orders": 0}

        domain = self._get_building_object_domain()
        action["domain"] = domain

        return action

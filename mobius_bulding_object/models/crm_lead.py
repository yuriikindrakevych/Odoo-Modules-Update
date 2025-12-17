#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools
from odoo import _
import logging
import json
_logger = logging.getLogger(__name__)


class Lead(models.Model):
    _inherit = "crm.lead"

    name_building_object = fields.Char("Name Building Object")
    building_object_id = fields.Many2one("building.object", "Building Object")

    # def action_set_lost(self, **additional_values):
    #     res = super().action_set_lost(**additional_values)
    #     lost_stage = self.env["crm.stage"].search([("name", "ilike", "lost")], 1)
    #     _logger.info("lost_stage=%s", lost_stage)
    #     if lost_stage:
    #         self.write({
    #             "stage_id": lost_stage.id,
    #         })
    #     return res


    def window_bulding_object_lead(self):
        view = self.env.ref("mobius_bulding_object.window_bulding_object_lead_form").id
        return {
                "type": "ir.actions.act_window",
                "name": _("Name Building Object"),
                "res_model": "crm.lead",
                "view_mode": "form",
                "res_id" : self.id,
                "views": [[view, "form"]],
                "target": "new",
        }

    def action_show_building_object(self):
        view = self.env.ref("mobius_bulding_object.view_building_object_form").id
        return {
                "type": "ir.actions.act_window",
                "name": _("Building Object"),
                "res_model": "building.object",
                "view_mode": "form",
                "res_id": self.building_object_id.id,
                "views": [[view, "form"]],
                "target": "form",
        }

    def create_window_bulding_object_lead_form(self):
        # _logger.debug("CRM LEAD  ID=%s", self.id)
        building_object_id = self.env["building.object"].create({
            "name": self.name_building_object,
            "crm_lead_id": self.id,
            "partner_id": self.partner_id.id,
            "user_id": self.user_id.id,
            "team_id": self.team_id.id,
            })
        self.building_object_id = building_object_id

    def action_new_quotation(self):
        action = super().action_new_quotation()
        if self.building_object_id:
            action['context']['default_building_object'] = self.building_object_id.id
        return action

#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from datetime import datetime, time

import logging

_logger = logging.getLogger(__name__)


class TodayTaskWizard(models.TransientModel):
    _name = "today.task.wizard"
    _transient = True

    name                            = fields.Char(default="Today Task", translate=True)
    count_today_lead                = fields.Integer(compute="_compute_count")
    count_today_calendar_meeting    = fields.Integer(compute="_compute_count")
    count_today_contact             = fields.Integer(compute="_compute_count")
    count_today_sale_order          = fields.Integer(compute="_compute_count")
    count_today_purchase_order      = fields.Integer(compute="_compute_count")

    def alternative_action(self):
        task_id = self.create({
            "name": _("Today Tasks"),
        })
        view = self.env.ref("mobius_lead_today_task_aklima.view_today_task_form").id
        return {
            "type" : "ir.actions.act_window",
            "res_model" : self._name,
            "res_id": task_id.id,
            "views": [[view, "form"]],
        }

    def get_count_lead(self):
        lead_task = self.env["crm.lead"].search_count([
            ("user_id", "=", self.env.user.id), 
            ("my_activity_date_deadline", "=", datetime.now().date().strftime("%Y-%m-%d"))
            ])
        return lead_task


    def get_count_today_calendar_meeting(self):
        lead_task = self.env["calendar.event"].search_count([
            ("partner_ids", "in", self.env.user.partner_id.id), 
            ("start", ">=", datetime.now().strftime("%Y-%m-%d 00:00:00")),
            ("start", "<=", datetime.now().strftime("%Y-%m-%d 23:23:59")),
            ("activity_type_id_real.category", "=", "meeting"),
            ])
        return lead_task

    def get_count_contact(self):
        lead_task = self.env["res.partner"].search_count([
            ("my_activity_date_deadline", "=", datetime.now().date().strftime("%Y-%m-%d"))
            ])
        return lead_task

    def get_count_sale_order(self):
        lead_task = self.env["sale.order"].search_count([
            ("user_id", "=", self.env.user.id), 
            ("my_activity_date_deadline", "=", datetime.now().date().strftime("%Y-%m-%d"))
            ])
        return lead_task

    def get_count_sale_purchase_order(self):
        lead_task = self.env["purchase.order"].search_count([
            ("user_id", "=", self.env.user.id), 
            ("my_activity_date_deadline", "=", datetime.now().date().strftime("%Y-%m-%d"))
            ])
        return lead_task

    def _compute_count(self):
        if not self.env.user:
            return
        self.count_today_lead = self.get_count_lead()
        self.count_today_contact = self.get_count_contact()
        self.count_today_sale_order = self.get_count_sale_order()
        self.count_today_purchase_order = self.get_count_sale_purchase_order()
        self.count_today_calendar_meeting = self.get_count_today_calendar_meeting()

    def action_open_lead(self):
        action = self.env["ir.actions.actions"]._for_xml_id("mobius_lead_today_task_aklima.crm_lead_action_my_activities_inherit")
        return action

    def action_calendar_list(self):
        action = self.env["ir.actions.actions"]._for_xml_id("mobius_lead_today_task_aklima.action_calendar_event_inherit")
        action["domain"] = [
            ("activity_type_id_real.category", "=", "meeting"),
            ("partner_ids", "in", self.env.user.partner_id.id),
        ]
        return action

    def action_open_contact(self):
        action = self.env["ir.actions.actions"]._for_xml_id("mobius_lead_today_task_aklima.contact_action_my_activities_inherit")
        return action

    def action_open_sale_order(self):
        action = self.env["ir.actions.actions"]._for_xml_id("mobius_lead_today_task_aklima.sale_action_my_activities_inherit")
        return action

    def action_open_purchase_order(self):
        action = self.env["ir.actions.actions"]._for_xml_id("mobius_lead_today_task_aklima.purchase_order_action_my_activities_inherit")
        return action
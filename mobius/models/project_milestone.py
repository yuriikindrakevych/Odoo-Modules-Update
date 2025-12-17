#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectMilestone(models.Model):
    _inherit = "project.milestone"

    task_ids       = fields.One2many("project.task", "milestone_id")
    num_tasks      = fields.Integer(compute="_compute_num_tasks", string="Num. tasks", store=True)
    num_incomplete = fields.Integer(compute="_compute_num_incomplete", string="Num. complete", store=True)

    @api.depends("task_ids")
    def _compute_num_tasks(self):
        for item in self:
            item.num_tasks = self.env["project.task"].search_count([("milestone_id", "=", item.id)])

    @api.depends("task_ids.stage_id")
    def _compute_num_incomplete(self):
        for item in self:
            item.num_incomplete = self.env["project.task"].search_count(["&", ("milestone_id", "=", item.id), ("stage_id.is_closed", "!=", True)])

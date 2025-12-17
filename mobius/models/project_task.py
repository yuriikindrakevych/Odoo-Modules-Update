#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    milestone_id = fields.Many2one("project.milestone", domain="[('project_id', '=', project_id)]")

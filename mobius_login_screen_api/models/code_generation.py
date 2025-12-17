#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import fields, models, api
import random
import string
from dateutil.relativedelta import *
import datetime
import logging
_logger = logging.getLogger(__name__)


class CodeGeneration(models.Model):
    _name = "code.generation"
    _description = "Code Generation"

    partner_id = fields.Many2one("res.partner", required=True, ondelete="restrict", index=True,
        string="Partner", help="Partner-related data of the user")

    phone = fields.Char(string="Phone")  # related="partner_id.phone",

    code_generation = fields.Char("Code", required=True, index=True)

    def _create_code(self):
        characters = string.digits
        code = ''.join(random.choice(characters) for i in range(8))
        return code

    def _create_random_string_upper_and_lower(self):
        # With combination of lower and upper case
        result_str = ''.join(random.choice(string.ascii_letters) for i in range(8))
        return result_str

    def pre_create(self, vals_list):
        for vals in vals_list:
            if vals.get("phone"):
                search_phone = self.search([("phone", "=", vals.get("phone"))])
                if search_phone:
                    search_phone.unlink()
        return self.create(vals_list)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["code_generation"] = self._create_code()
        item = super(CodeGeneration, self).create(vals_list)
        return item

    def write(self, vals):
        if vals.get("code_generation") is False:
            vals["code_generation"] = self._create_code()
        vals["create_date"] = fields.datetime.now()
        result = super(CodeGeneration, self).write(vals)
        return result

    def get_code_suitable(self, phone, code):
        record = self.search([("phone", "=", phone), ("code_generation", "=", code)], limit=1)
        if record:
            minutes = self.get_how_long_does_the_record_exist_in_minutes(record)
            if minutes > 10:
                record.unlink()
                return False
            else:
                return True
        else:
            return False

    def get_code(self, phone, code):
        record = self.search([("phone", "=", phone), ("code_generation", "=", code)], limit=1)
        return record

    def scheduler_cleaning(self):
        self = self.search([]).sorted(lambda m: (m.create_date))
        next_first_record_for_delete = []
        next_first_record = False
        for record in self:
            minutes = self.get_how_long_does_the_record_exist_in_minutes(record)
            if minutes > 10:
                record.unlink()
            else:
                if not next_first_record:
                    next_first_record_for_delete.append(record)
                    next_first_record = True
        if len(next_first_record_for_delete) > 0 and next_first_record:
            new_time_to_run_scheduler = next_first_record_for_delete[0].create_date + datetime.timedelta(minutes=11)
            id_cron = self.env.ref("mobius_login_screen_api.code_generation_action_ir_cron").id
            search_scheduler = self.env["ir.cron"].search([("id", "=", id_cron)])
            if search_scheduler:
                search_scheduler.nextcall = new_time_to_run_scheduler

    def get_how_long_does_the_record_exist_in_minutes(self, record):
        if record:
            start_dt = fields.Datetime.from_string(record.create_date)
            finish_dt_field = fields.datetime.now()
            finish_dt = fields.Datetime.from_string(finish_dt_field)
            difference = relativedelta(finish_dt, start_dt)
            minutes = difference.minutes
            return minutes
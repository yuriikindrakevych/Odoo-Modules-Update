#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import fields, models
from dateutil.relativedelta import *
import datetime
class MobiusSession(models.Model):
    _name = "mobius.session"

    session_id = fields.Char("Session ID")
    db_name = fields.Char("DB name")
    login = fields.Char("Login")
    password = fields.Char("Password")

    def get_how_long_does_the_record_exist_in_minutes(self, record):
        if record:
            start_dt = fields.Datetime.from_string(record.create_date)
            finish_dt_field = fields.datetime.now()
            finish_dt = fields.Datetime.from_string(finish_dt_field)
            difference = relativedelta(finish_dt, start_dt)
            minutes = difference.minutes
            return minutes

    def scheduler_cleaning(self):
        self = self.search([]).sorted(lambda m: (m.create_date))
        for record in self:
            minutes = self.get_how_long_does_the_record_exist_in_minutes(record)
            if minutes > 5:
                record.unlink()
#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)


class Lead(models.Model):
    _inherit = "crm.lead"

    ignore_on_create = fields.Boolean(default=True)

    def _create_activities_and_events(self, record):
        _logger.info("Starting _create_activities_and_events for record %s with context %s", record.id,
                     self.env.context)

        future_date = datetime.now() + timedelta(days=1)
        future_stop_date = future_date + timedelta(hours=1)
        mail_activity = self.env["mail.activity"].sudo().create({
            "res_name": record.name,
            "activity_type_id": self.env.ref('mail.mail_activity_data_call').id,
            "summary": record.name,
            "res_model_id": self.env["ir.model"]._get("crm.lead").id,
            "res_id": record.id,
            "date_deadline": future_date.strftime("%Y-%m-%d"),
            "user_id": record.user_id.id or self.env.uid,
            "automated": True,
            "note": record.description,
        })

        # self.env["calendar.event"].sudo().create({
        #     "res_id": record.id,
        #     "opportunity_id": record.id,
        #     "name": record.name,
        #     "recurrence_update": "self_only",
        #     "active": True,
        #     "activity_type_id": self.env.ref('mail.mail_activity_data_call').id,
        #     "activity_type_id_real": self.env.ref('mail.mail_activity_data_call').id,
        #     "user_id": record.user_id.id or self.env.uid,
        #     "activity_ids": [(6, 0, [mail_activity.id])],
        #     "partner_ids": [(6, 0, [record.user_id.partner_id.id])],
        #     "res_model": "crm.lead",
        #     "res_model_id": self.env["ir.model"]._get("crm.lead").id,
        #     "allday": True,
        #     "start": future_date.strftime('%Y-%m-%d %H:%M:%S'),
        #     "stop": future_stop_date.strftime('%Y-%m-%d %H:%M:%S'),
        #     "duration": 1.0,
        # })

    def _find_existing_leads(self, vals):
        search_fields = ["mobile", "phone", "email_from", "vat"]

        for field in search_fields:
            if field in vals and vals[field] not in [None, False, ""]:
                leads = self.env["crm.lead"].search(
                    [(field, "=", vals[field])]
                )
                if leads:
                    return leads
        return None

    @api.model
    def _check_import_consistency(self, vals_list):
        vals_create_list = []
        vals_write_list = []
        for vals in vals_list:
            _logger.info("vals=%s", vals)

            existing_leads = self._find_existing_leads(vals)
            if existing_leads:
                vals_write_list.append(vals)
            else:
                vals_create_list.append(vals)

        return vals_create_list, vals_write_list

    @api.model_create_multi
    def create(self, vals_list):
        _logger.info("lead -> create")
        _logger.info("self.env.context.get('skip_check_import')=%s", self.env.context.get("skip_check_import"))
        new_vals_list = vals_list
        writed_records = []
        if self.env.context.get("import_file"):
            new_vals_list = []
            for vals in vals_list:
                existing_leads = self._find_existing_leads(vals)
                _logger.info("existing_leads=%s", existing_leads)
                if not existing_leads:
                    new_vals_list.append(vals)
                else:
                    _logger.info("LEAD EXIST")
                    for lead in existing_leads:
                        _logger.info("TRY TO WRITE")
                        _logger.info("lead=%s", lead)
                        _logger.info("vals=%s", vals)

                        lead.write(vals)
                        writed_records.append(lead.id)
                        self._create_activities_and_events(lead)

        _logger.info("new_vals_list=%s", new_vals_list)
        if not new_vals_list:
            _logger.info("EMPTY DATA")
            if writed_records:
                return self.browse(writed_records)

            return self.browse()
        results = super().create(new_vals_list)
        if self.env.context.get("import_file"):
            for res in results:
                self._create_activities_and_events(res)
        return results

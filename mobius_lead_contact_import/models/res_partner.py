#!/usr/bin/python3
# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime
import pytz

CONTACT_SEARCH_FIELDS = ["mobile", "phone", "email", "vat"]
CHARS_TO_DELETE = ";_ "
ALWAYS_UPDATE_FIELDS = {"source_id"}


class ResPartner(models.Model):
    _inherit = "res.partner"

    source_id = fields.Many2one(comodel_name="utm.source")
    email_formatted = fields.Char(compute="_compute_email_formatted", store=True, readonly=True)

    @staticmethod
    def _get_formatted_email(email):
        if not email:
            return False
        delete_map = str.maketrans("", "", CHARS_TO_DELETE)
        return email.translate(delete_map)

    @api.depends("email")
    def _compute_email_formatted(self):
        for record in self:
            record.email_formatted = self._get_formatted_email(record.email)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get("import_lead"):
            return super().create(vals_list)

        import_file = self.env.context.get("import_file")
        if not import_file:
            return super().create(vals_list)

        new_vals_list = []
        wrote_records = []

        for vals in vals_list:
            existing_contacts = self._find_existing_contacts(vals)
            if not existing_contacts:
                self._add_lead_tag_to_vals(vals)
                new_vals_list.append(vals)
            else:
                for contact in existing_contacts:
                    self._update_contact_fields(contact, vals)
                    wrote_records.append(contact.id)
                    self._create_activity(contact, vals.get("comment", ""))

        results = self.browse()
        if new_vals_list:
            results = super().create(new_vals_list)
            for res in results:
                # For new contacts, get the comment from the vals that created this record
                comment_for_activity = ""
                for vals in new_vals_list:
                    if vals.get("name") == res.name:  # Match by name or other identifier
                        comment_for_activity = vals.get("comment", "")
                        break
                self._create_activity(res, comment_for_activity)

        # Return first updated contact if no new contacts created (for autocomplete compatibility)
        return results if results else self.browse(wrote_records[0]) if wrote_records else self.browse()

    @api.model
    def _create_activity(self, record, new_comment=None):
        record.ensure_one()
        activity_type = self.env.ref("mail.mail_activity_data_call", raise_if_not_found=False)
        if not activity_type:
            return

        self.env["mail.activity"].with_context(mail_activity_quick_update=True).sudo().create({
            "res_name": record.name or "Contact",
            "activity_type_id": activity_type.id,
            "summary": record.name or "New Contact",
            "res_model_id": self.env["ir.model"]._get("res.partner").id,
            "res_id": record.id,
            "date_deadline": datetime.now(pytz.timezone("Europe/Warsaw")).strftime("%Y-%m-%d"),
            "user_id": record.user_id.id or self.env.uid,
            "automated": True,
            "note": new_comment or "",
        })

    @api.model
    def _find_existing_contacts(self, vals):
        domain_conditions = []

        for field in CONTACT_SEARCH_FIELDS:
            value = vals.get(field)
            if value:  # Simplified check
                if field == "email":
                    formatted_email = self._get_formatted_email(value)
                    if formatted_email:
                        domain_conditions.append(("email_formatted", "=", formatted_email))
                else:
                    domain_conditions.append((field, "=", value))

        if not domain_conditions:
            return None

        # Build OR domain efficiently
        domain = ["|"] * (len(domain_conditions) - 1) + domain_conditions if len(
            domain_conditions) > 1 else domain_conditions
        contacts = self.search(domain)
        return list(contacts) if contacts else None

    @api.model
    def _add_lead_tag_to_vals(self, vals):
        lead_tag = self.env.ref("mobius_lead_contact_import.res_partner_category_lead", raise_if_not_found=False)
        if not lead_tag:
            return

        add_lead_tag_command = (4, lead_tag.id, 0)
        category_ids = vals.get("category_id", [])

        if not category_ids:
            vals["category_id"] = [add_lead_tag_command]
        elif isinstance(category_ids, list) and not self._check_vals_lead_tag_existence(vals, lead_tag.id):
            vals["category_id"].append(add_lead_tag_command)

    @staticmethod
    def _check_vals_lead_tag_existence(vals, lead_tag_id):
        category_commands = vals.get("category_id", [])
        if not isinstance(category_commands, list):
            return False

        for command in category_commands:
            if not isinstance(command, (list, tuple)) or len(command) != 3:
                continue
            # Check direct ID match or ID in collection
            if command[1] == lead_tag_id or (isinstance(command[2], (list, tuple)) and lead_tag_id in command[2]):
                return True
        return False

    @staticmethod
    def _update_contact_fields(contact, vals):
        contact.ensure_one()
        new_vals = {}

        for field_name, value in vals.items():
            if field_name not in contact._fields:
                continue

            if field_name == "comment":
                existing_comment = contact.comment or ""
                new_comment = value or ""

                if new_comment:
                    timestamp = datetime.now(pytz.timezone("Europe/Warsaw")).strftime("%Y-%m-%d %H:%M")
                    if existing_comment:
                        new_vals[field_name] = f"{existing_comment}\n\n[{timestamp}] {new_comment}"
                    else:
                        new_vals[field_name] = f"[{timestamp}] {new_comment}"
            elif not contact[field_name] or field_name in ALWAYS_UPDATE_FIELDS:
                new_vals[field_name] = value

        if new_vals:
            contact.write(new_vals)

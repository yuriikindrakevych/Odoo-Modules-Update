import logging
from datetime import timedelta, datetime
import pytz
from markupsafe import Markup
from dateutil.relativedelta import relativedelta

from odoo import _, models, fields, api
from ..tools import phone_parser, email_formatter

_logger = logging.getLogger(__name__)

CONTACT_LEAD_DUPLICATE_CHECK_FIELDS = ["mobile_national_significant", "phone_national_significant", "email_formatted"]
PHONE_NATIONAL_FIELDS = ["mobile_national_significant", "phone_national_significant"]
EMAIL_FORMATTED = "email_formatted"


class GoogleSheetImporter(models.Model):
    _inherit = "google.sheet.importer"

    mapping_model_is_contact = fields.Boolean(compute="_compute_mapping_model_is_contact", store=True)
    user_id = fields.Many2one(comodel_name="res.users", string="Salesperson")
    source_id = fields.Many2one(comodel_name="utm.source", string="Lead Source")
    category_ids = fields.Many2many(comodel_name="res.partner.category")

    @api.depends("mapping_model_id")
    def _compute_mapping_model_is_contact(self):
        partner_model = self.env.ref("base.model_res_partner", raise_if_not_found=False)
        for record in self:
            record.mapping_model_is_contact = record.mapping_model_id == partner_model

    def _sync_cron_with_importer(self, changed_fields):
        """
        Synchronize changes in the importer model with the related ir.cron record.

        :param changed_fields: Set of fields that were modified in the write operation.
        """
        # Fields that are important for ir.cron synchronization
        relevant_fields = {"interval_type", "interval_number", "active"}

        # Determine which relevant fields have been changed
        fields_to_update = relevant_fields & changed_fields

        if fields_to_update:
            # Prepare values to update only the changed relevant fields
            update_vals = {field: self[field] for field in fields_to_update}

            # If interval_number or interval_type changed, update nextcall
            if {"interval_number", "interval_type"} & changed_fields:
                now = fields.Datetime.now()

                # Calculate the next execution time based on interval
                if self.interval_type == "minutes":
                    next_call = now + timedelta(minutes=self.interval_number)
                elif self.interval_type == "hours":
                    next_call = now + timedelta(hours=self.interval_number)
                elif self.interval_type == "days":
                    next_call = now + timedelta(days=self.interval_number)
                elif self.interval_type == "weeks":
                    next_call = now + timedelta(weeks=self.interval_number)
                elif self.interval_type == "months":
                    next_call = now + relativedelta(months=self.interval_number)
                else:
                    # Default to minutes if interval_type is not recognized
                    next_call = now + timedelta(months=self.interval_number)

                update_vals["nextcall"] = next_call

            self.cron_id.write(update_vals)

    def _prepare_constant_fields(self):
        self.ensure_one()
        return {
            "user_id": self.user_id.id if self.user_id else False,
            "source_id": self.source_id.id if self.source_id else False,
            "category_id": self.category_ids.ids if self.category_ids else [],
        }

    def execute_import(self):
        """
        Method called by the associated ir.cron record or manually to import data from the Google Sheet.
        """
        import_contact_recs = self.filtered(lambda rec: rec.mapping_model_is_contact)
        contact_lead_tag_mapping = self.create_absent_tags_and_get_contact_lead_tag_mapping(import_contact_recs)

        for record in self:

            # try:
            constant_fields = record._prepare_constant_fields()
            worksheet = record._get_worksheet()

            # Fetch all rows from the sheet
            rows = worksheet.get_all_records()
            mappings = self.field_mapping_ids

            contacts_mapping, leads_mapping = {}, {}
            if record.mapping_model_is_contact:
                contacts_mapping, leads_mapping = self.get_contact_details_records_mapping(rows, mappings)

            # Check if "Imported" column exists, if not, add it
            headers = worksheet.row_values(1)
            if "Imported" not in headers:
                worksheet.update_cell(1, len(headers) + 1, "Imported")
                headers.append("Imported")

            imported_col_index = headers.index("Imported") + 1
            imported_count = 0
            skipped_count = 0
            processed_count = 0

            for i, row in enumerate(rows, start=2):  # Start at row 2 to skip headers
                processed_count += 1  # Increment the processed row count

                record_data = {}
                skip_record = False
                reasons = []

                # Skip rows already marked as imported
                if row.get("Imported") == "TRUE":
                    continue

                duplicate_contacts = self.env["res.partner"]
                duplicate_leads = self.env["crm.lead"]
                for mapping in mappings:
                    sheet_value = row.get(mapping.sheet_header)

                    # If mandatory field is missing, skip this row and log the issue
                    if mapping.mandatory and not sheet_value:
                        reasons.append(f"Mandatory field '{mapping.sheet_header}' is missing.")
                        skip_record = True

                    if mapping.duplicate_check and sheet_value and mapping.odoo_field.name not in CONTACT_LEAD_DUPLICATE_CHECK_FIELDS:
                        existing_record = self.env[self.mapping_model_id.model].search(
                            [(mapping.odoo_field.name, '=', sheet_value)], limit=1)
                        if existing_record:
                            reasons.append(f"Duplicate value '{sheet_value}' for field '{mapping.sheet_header}'.")
                            skip_record = True

                    # Map the value to the Odoo field
                    if mapping.odoo_field:
                        fname = mapping.odoo_field.name
                        if record.mapping_model_is_contact and fname in CONTACT_LEAD_DUPLICATE_CHECK_FIELDS:
                            formatted_value = None
                            if fname in PHONE_NATIONAL_FIELDS:
                                formatted_value = phone_parser.get_national_significant(sheet_value)
                            elif fname == EMAIL_FORMATTED:
                                formatted_value = email_formatter.get_formatted_email(sheet_value)
                            if contacts_mapping.get(formatted_value):
                                duplicate_contacts |= contacts_mapping.get(formatted_value)
                            if leads_mapping.get(formatted_value):
                                duplicate_leads |= leads_mapping.get(formatted_value)

                        record_data[fname] = sheet_value

                if record.mapping_model_is_contact:
                    res = record.import_contacts_with_duplicates_data(
                        record_data, duplicate_contacts, duplicate_leads, contact_lead_tag_mapping
                    )
                    skip_record = True if res else skip_record
                    if skip_record:
                        duplicate_in_modules = []
                        if duplicate_contacts:
                            duplicate_in_modules.append("contact(res.partner)")
                        if duplicate_leads:
                            duplicate_in_modules.append("lead(crm.lead)")
                        reasons.append(f"Found duplicate in {' and '.join(duplicate_in_modules)} module(s).")

                if skip_record:
                    if record.mapping_model_is_contact:
                        self._create_import_activity(None, None, duplicate_contacts, duplicate_leads)

                    skipped_count += 1
                    _logger.warning(
                        "Row %s skipped for Model '%s', Import '%s'. Reasons: %s",
                        i, self.mapping_model_id.model, self.name, "; ".join(reasons)
                    )
                    worksheet.update_cell(i, imported_col_index, "FALSE")
                    continue

                # Create the record in Odoo
                if record.mapping_model_is_contact:
                    record_data.update(constant_fields)
                    # comment for res.partner and description for crm.lead
                    # comment = record_data.get("comment") or record_data.get("description")
                    # new_contact, new_lead = None, None
                    # if "comment" in record_data:
                    #     del record_data["comment"]
                    # if "description" in record_data:
                    #     del record_data["comment"]
                    if not record_data.get("name"):
                        record_data["name"] = _("Imported")
                    # if duplicate contacts exist here, then there's a duplicate in company
                    # that's why we use it, to create and link a new lead
                    contact_rec_set = duplicate_contacts or self.env["res.partner"].create(record_data)

                    # create note only if new record
                    new_contact, new_lead = None, None
                    if not duplicate_contacts and contact_rec_set:
                        # contact_rec_set._create_activity_google_sheet()
                        new_contact = contact_rec_set
                        # self._create_import_note(record_data, contact_rec_set)
                    if contact_rec_set:
                        new_lead = record.create_lead(record_data, contact_rec_set, contact_lead_tag_mapping)
                        # self._create_import_note(record_data, new_lead)

                    self._create_import_activity(new_contact, new_lead, duplicate_contacts, duplicate_leads)
                else:
                    self.env[self.mapping_model_id.model].create(record_data)
                imported_count += 1
                worksheet.update_cell(i, imported_col_index, "True")

            _logger.info(
                "Import completed for Model '%s', Import '%s'. Imported: %d, Skipped: %d",
                self.mapping_model_id.model, self.name, imported_count, skipped_count
            )

            record.message_post(
                body=Markup(
                    f"Import Summary:<br/>"
                    f"Imported: {imported_count}<br/>"
                    f"Skipped: {skipped_count}<br/>"
                    f"Total Rows in Sheet: {len(rows)}<br/>"
                    f"Total Rows Processed: {processed_count}<br/>"
                )
            )

            # except Exception as e:
            #     _logger.error(
            #         "Error while importing from Google Sheets for Model '%s', Import '%s': %s",
            #         self.mapping_model_id.model, self.name, e
            #     )
            #     record.message_post(body=f"Error during import: {e}")

    def create_absent_tags_and_get_contact_lead_tag_mapping(self, records):
        category_ids = records.category_ids
        crm_tags = self.env["crm.tag"].search([("name", "in", category_ids.mapped("name"))])
        contact_lead_tag_mapping = {tag.name: tag.id for tag in crm_tags}
        create_vals = [{"name": tag.name, "color": tag.color} for tag in category_ids
                       if tag.name not in contact_lead_tag_mapping]

        contact_lead_tag_mapping.update({tag.name: tag.id for tag in self.env["crm.tag"].create(create_vals)})
        return contact_lead_tag_mapping

    @api.model
    def get_contact_details_records_mapping(self, rows, mappings):
        duplicate_check_data = dict()
        contacts_mapping, leads_mapping = {}, {}
        filtered_mappings = mappings.filtered(
                lambda mapp: mapp.odoo_field and mapp.odoo_field.name in CONTACT_LEAD_DUPLICATE_CHECK_FIELDS
        )
        for row in rows:
            for mapping in filtered_mappings:
                fname = mapping.odoo_field.name
                sheet_value = row.get(mapping.sheet_header)
                formatted_value = None
                if fname in PHONE_NATIONAL_FIELDS:
                    formatted_value = phone_parser.get_national_significant(sheet_value)
                elif fname == EMAIL_FORMATTED:
                    formatted_value = email_formatter.get_formatted_email(sheet_value)
                if not formatted_value:
                    continue
                if fname not in duplicate_check_data:
                    duplicate_check_data[fname] = set()
                duplicate_check_data[fname].add(formatted_value)

        if not duplicate_check_data:
            return contacts_mapping, leads_mapping

        domain: list = ["|"] * (len(duplicate_check_data) - 1)
        domain.extend([(fname, "in", list(value)) for fname, value in duplicate_check_data.items()])
        contact_model, lead_model = self.env["res.partner"], self.env["crm.lead"]
        contacts = contact_model.search(domain)
        leads = lead_model.search(domain)
        for contact in contacts:
            if contact.mobile_national_significant:
                contacts_mapping.setdefault(contact.mobile_national_significant, contact_model.browse())
                contacts_mapping[contact.mobile_national_significant] |= contact
            if contact.phone_national_significant:
                contacts_mapping.setdefault(contact.phone_national_significant, contact_model.browse())
                contacts_mapping[contact.phone_national_significant] |= contact
            if contact.email_formatted:
                contacts_mapping.setdefault(contact.email_formatted, contact_model.browse())
                contacts_mapping[contact.email_formatted] |= contact

        for lead in leads:
            if lead.mobile_national_significant:
                leads_mapping.setdefault(lead.mobile_national_significant, lead_model.browse())
                leads_mapping[lead.mobile_national_significant] |= lead
            if lead.phone_national_significant:
                leads_mapping.setdefault(lead.phone_national_significant, lead_model.browse())
                leads_mapping[lead.phone_national_significant] |= lead
            if lead.email_formatted:
                leads_mapping.setdefault(lead.email_formatted, lead_model.browse())
                leads_mapping[lead.email_formatted] |= lead

        return contacts_mapping, leads_mapping

    def import_contacts_with_duplicates_data(
            self, record_data, duplicate_contacts, duplicate_leads, contact_lead_tag_mapping
    ):
        if not duplicate_contacts and not duplicate_leads:
            return False

        phone_national_significant = record_data.get("phone_national_significant")
        mobile_national_significant = record_data.get("mobile_national_significant")
        email_formatted = record_data.get("email_formatted")
        # comment = record_data.get("comment") or record_data.get("description")
        # today_date_str = datetime.now(pytz.timezone("Europe/Warsaw")).strftime("%Y-%m-%d")
        only_companies = True

        for contact in duplicate_contacts:
            if not contact.is_company:
                only_companies = False

            write_vals = {}

            if not contact.phone and phone_national_significant:
                write_vals["phone"] = phone_national_significant
            if not contact.mobile and mobile_national_significant:
                write_vals["mobile"] = mobile_national_significant
            if not contact.email and email_formatted:
                write_vals["email"] = email_formatted

            if self.category_ids:
                write_vals["category_id"] = [fields.Command.link(tag_id) for tag_id in self.category_ids.ids]
            contact.write(write_vals)

            # note_body = _("Contact data updated from Google Sheet import on %s.", today_date_str)
            # contact.message_post(body=note_body, message_type="notification", subtype_xmlid="mail.mt_note")
            # if comment:
            self._create_import_note(record_data, contact)
            # summary = _("Found this contact as duplicate during import. Reminding you about it.")
            # self._create_import_activity(contact, summary)

        for lead in duplicate_leads:
            write_vals = {}

            if not lead.phone and phone_national_significant:
                write_vals["phone"] = phone_national_significant
            if not lead.mobile and mobile_national_significant:
                write_vals["mobile"] = mobile_national_significant
            if not lead.email_from and email_formatted:
                write_vals["email_from"] = email_formatted

            if self.category_ids:
                write_command = [fields.Command.link(contact_lead_tag_mapping.get(tag.name))
                                 for tag in self.category_ids if tag.name in contact_lead_tag_mapping]

                write_vals["tag_ids"] = write_command

            lead.write(write_vals)

            # note_body = _("Lead data updated from Google Sheet import on %s.", today_date_str)
            # lead.message_post(body=note_body, message_type="notification", subtype_xmlid="mail.mt_note")
            # if comment:
            self._create_import_note(record_data, lead)
            # summary = _("Found this lead as duplicate during import. Reminding you about it.")
            # self._create_import_activity(lead, summary)

        return False if not duplicate_leads and only_companies else True

    def create_lead(self, record_data, contact_rec_set, contact_lead_tag_mapping):
        create_vals = {"type": "lead", "priority": "1"}

        if record_data.get("phone_national_significant"):
            create_vals["phone"] = record_data.get("phone_national_significant")
        if record_data.get("mobile_national_significant"):
            create_vals["mobile"] = record_data.get("mobile_national_significant")
        if record_data.get("email_formatted"):
            create_vals["email_from"] = record_data.get("email_formatted")
        create_vals["partner_id"] = contact_rec_set[0].id if contact_rec_set else False
        # using self of record data because iteration through the categories is needed
        if self.category_ids:
            write_command = [fields.Command.link(contact_lead_tag_mapping.get(tag.name))
                             for tag in self.category_ids if tag.name in contact_lead_tag_mapping]

            create_vals["tag_ids"] = write_command
        create_vals["name"] = record_data.get("name") or "No name provided"
        if record_data.get("user_id"):
            create_vals["user_id"] = record_data.get("user_id")
        if record_data.get("source_id"):
            create_vals["source_id"] = record_data.get("source_id")

        lead = self.env["crm.lead"].create(create_vals)
        note_body = _("Lead has been imported %s.", datetime.now(pytz.timezone("Europe/Warsaw")).strftime("%Y-%m-%d"))
        lead.message_post(body=note_body, message_type="notification", subtype_xmlid="mail.mt_note")
        # summary = _("Created lead during import.")
        # self._create_import_activity(lead, summary)
        return lead

    def _create_import_activity(
            self, new_contact, new_lead, duplicate_contacts, duplicate_leads
    ):
        activity_type = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        if not activity_type:
            _logger.warning("Activity type 'Data To-Do' not found. Cannot create activity.")
            return

        record = None
        summary = _("During import from sheet %s: ", self.worksheet_name)
        add_to_summary = []
        if new_contact:
            record = new_contact
            add_to_summary.append(_("Created contact: %s", new_contact.name))
        if new_lead:
            record = new_lead if not record else record
            add_to_summary.append(_("Created lead: %s", new_lead.name))
        if duplicate_contacts:
            record = duplicate_contacts[0] if not record else record
            add_to_summary.append(_("Found duplicate contact(s): %s", ", ".join(duplicate_contacts.mapped("name"))))
        if duplicate_leads:
            record = duplicate_leads[0] if not record else record
            add_to_summary.append(_("Found duplicate lead(s): %s", ", ".join(duplicate_leads.mapped("name"))))
        summary += "; ".join(add_to_summary) if add_to_summary else ""

        if not record:
            return

        self.env["mail.activity"].sudo().create({
            "res_model_id": self.env["ir.model"]._get_id(record._name),
            "res_id": record.id,
            "activity_type_id": activity_type.id,
            "summary": Markup(summary or _("Follow up on imported data")),
            "user_id": record.user_id.id or self.user_id.id or False,
            "date_deadline": datetime.now(pytz.timezone("Europe/Warsaw")).strftime("%Y-%m-%d"),
            "automated": True,
        })

    def _create_import_note(self, record_data: dict, record):
        note_body = f"{self.worksheet_name}"
        if self.category_ids:
            note_body += f"<br/>{' '.join(self.category_ids.mapped('name'))}"
        for f_name, f_value in record_data.items():
            if not f_value or f_name in ["user_id", "source_id", "category_id"]:
                continue
            note_body += f"<br/>{f_name}: {f_value}"
        record.message_post(body=Markup(note_body), message_type="notification", subtype_xmlid="mail.mt_note")

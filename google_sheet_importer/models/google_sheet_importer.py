from odoo import models, fields, api
import base64
import logging
from markupsafe import Markup
import gspread
_logger = logging.getLogger(__name__)

class GoogleSheetImporter(models.Model):
    """
    Model for importing data from Google Sheets into Odoo.
    This model is integrated with ir.cron to schedule periodic imports.
    """
    _name = "google.sheet.importer"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {"ir.cron": "cron_id"}
    _description = "Google Sheet Importer"

    # Fields specific to Google Sheet Importer
    service_account_credentials = fields.Binary(
        string='Service Account Credentials', required=True,
        help="Upload the JSON credentials file for the Google Service Account."
    )
    google_sheet_id = fields.Char(
        string='Google Sheet ID', required=True, help="The unique ID of the Google Sheet to import data from."
    )
    worksheet_name = fields.Char(
        string='Worksheet Name', default='Sheet1', required=True,
        help="The name of the worksheet within the Google Sheet."
    )
    mapping_model_id = fields.Many2one(
        'ir.model', string='Target Model', required=True, ondelete="cascade",
        help="Specify the Odoo model where data will be imported."
    )
    field_mapping_ids = fields.One2many(
        'google.sheet.field.mapping', 'import_id', string="Field Mappings",
        help="Define the mapping between Google Sheet columns and Odoo fields."
    )

    # Inherited field from ir.cron
    cron_id = fields.Many2one("ir.cron", required=True, ondelete="cascade")
    active = fields.Boolean(string='Active', default=True, help="Activate or deactivate the importer.")

    def _sync_cron_with_importer(self, changed_fields):
        """
        Synchronize changes in the importer model with the related ir.cron record.

        :param changed_fields: Set of fields that were modified in the write operation.
        """
        # Fields that are important for ir.cron synchronization
        relevant_fields = {'interval_type', 'interval_number', 'active'}

        # Determine which relevant fields have been changed
        fields_to_update = relevant_fields & changed_fields

        if fields_to_update:
            # Prepare values to update only the changed relevant fields
            update_vals = {field: self[field] for field in fields_to_update}
            self.cron_id.write(update_vals)

    @api.model
    def default_get(self, fields):
        """
        Provide default values for new records, including the related model ID.

        :param fields: List of fields to populate.
        :return: Dictionary of default values.
        """
        defaults = super(GoogleSheetImporter, self).default_get(fields)
        defaults['model_id'] = self.env['ir.model'].search([('model', '=', self._name)]).id
        defaults['numbercall'] = -1
        return defaults

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override the create method to initialize the associated ir.cron record.

        :param vals: Dictionary of values for the new record.
        :return: Newly created GoogleSheetImporter record.
        """
        # Create the Google Sheet Importer record
        records = super(GoogleSheetImporter, self).create(vals_list)

        # Initialize the associated ir.cron record
        for record in records:
            record.cron_id.write({
                'code': f"env['google.sheet.importer'].browse({record.id}).execute_import()",
            })

        return records

    def write(self, vals):
        """
        Override the write method to synchronize changes with the related ir.cron.

        :param vals: Dictionary of values to update.
        :return: True if the write operation was successful.
        """
        res = super(GoogleSheetImporter, self).write(vals)
        self._sync_cron_with_importer(set(vals.keys()))
        return res

    def unlink(self):
        """
        Override the unlink method to ensure the associated ir.cron record is also deleted.

        :return: True if the unlink operation was successful.
        """
        self.mapped('cron_id').unlink()
        return super(GoogleSheetImporter, self).unlink()

    def _get_worksheet(self):
        if not self.service_account_credentials:
            _logger.error("Service account credentials are missing for import '%s'.", self.name)

        credentials_data = base64.b64decode(self.service_account_credentials)
        client = gspread.service_account_from_dict(eval(credentials_data.decode('utf-8')))
        sheet = client.open_by_key(self.google_sheet_id)
        return sheet.worksheet(self.worksheet_name)

    def execute_import(self):
        """
        Method called by the associated ir.cron record or manually to import data from the Google Sheet.
        """
        for record in self:

            try:
                worksheet = record._get_worksheet()

                # Fetch all rows from the sheet
                rows = worksheet.get_all_records()
                mappings = self.field_mapping_ids

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

                    for mapping in mappings:
                        sheet_value = row.get(mapping.sheet_header)

                        # If mandatory field is missing, skip this row and log the issue
                        if mapping.mandatory and not sheet_value:
                            reasons.append(f"Mandatory field '{mapping.sheet_header}' is missing.")
                            skip_record = True

                        # Check for duplicates if enabled
                        if mapping.duplicate_check and sheet_value:
                            existing_record = self.env[self.mapping_model_id.model].search(
                                [(mapping.odoo_field.name, '=', sheet_value)], limit=1)
                            if existing_record:
                                reasons.append(f"Duplicate value '{sheet_value}' for field '{mapping.sheet_header}'.")
                                skip_record = True

                        # Map the value to the Odoo field
                        if mapping.odoo_field:
                            record_data[mapping.odoo_field.name] = sheet_value

                    if skip_record:
                        skipped_count += 1
                        _logger.warning(
                            "Row %s skipped for Model '%s', Import '%s'. Reasons: %s",
                            i, self.mapping_model_id.model, self.name, "; ".join(reasons)
                        )
                        worksheet.update_cell(i, imported_col_index, "FALSE")
                        continue

                    # Create the record in Odoo
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

            except Exception as e:
                _logger.error(
                    "Error while importing from Google Sheets for Model '%s', Import '%s': %s",
                    self.mapping_model_id.model, self.name, e
                )
                record.message_post(body=f"Error during import: {e}")

    def action_fetch_headers(self):
        """
        Fetch headers from Google Sheet and update the field mappings accordingly.

        This method:
        1. Fetches headers from the specified Google Sheet and worksheet.
        2. Updates the field mappings in Odoo based on the sheet headers.
        3. Creates new mappings for any headers not yet mapped to Odoo fields.
        4. Removes mappings for headers no longer available in the sheet.
        """
        for record in self:
            try:
                # Fetch headers from Google Sheet
                worksheet = record._get_worksheet()
                headers = worksheet.row_values(1)  # Assuming headers are in the first row

                # Get existing field mappings
                existing_mappings = record.field_mapping_ids

                # Create a dictionary of existing field mappings for fast lookup by sheet header
                existing_header_mapping = {mapping.sheet_header: mapping for mapping in existing_mappings}

                # List of field mappings to create or update
                to_create_or_update = []

                # Iterate through the headers from the sheet
                for index, header in enumerate(headers):
                    # Skip if header is already mapped to an Odoo field
                    existing_mapping = existing_header_mapping.get(header)
                    if existing_mapping:
                        # If already mapped and header is present, just update its sequence
                        existing_mapping.sequence = index + 1
                        to_create_or_update.append(existing_mapping)
                        # Remove from the dictionary so we can identify fields to remove
                        del existing_header_mapping[header]
                    else:
                        # Create a new mapping for this header if it is not already mapped
                        new_mapping = {
                            'import_id': record.id,
                            'sequence': index + 1,
                            'sheet_header': header,
                        }
                        to_create_or_update.append(new_mapping)

                # Remove mappings that no longer exist in the sheet (headers removed from the sheet)
                for header, mapping in existing_header_mapping.items():
                    mapping.unlink()

                # Create or update the new mappings
                for mapping_data in to_create_or_update:
                    if isinstance(mapping_data, dict):
                        record.field_mapping_ids.create(mapping_data)
                        _logger.info("New field mapping created for header '%s'.", mapping_data['sheet_header'])
                    else:
                        # Update the sequence for existing mappings
                        mapping_data.write({'sequence': mapping_data.sequence})
                        _logger.info("Field mapping updated for header '%s'.", mapping_data.sheet_header)

            except Exception as e:
                _logger.error("Error while fetching headers from Google Sheets for Import '%s': %s", record.name, e)

        return True
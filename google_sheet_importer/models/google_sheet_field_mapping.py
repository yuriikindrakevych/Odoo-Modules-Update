from odoo import api, fields, models
from odoo.exceptions import ValidationError


class GoogleSheetFieldMapping(models.Model):
    """
    Represents the mapping of fields between a Google Sheet and Odoo.
    This model allows specifying how data in a Google Sheet maps to fields in an Odoo model.
    """
    _name = 'google.sheet.field.mapping'
    _description = 'Google Sheet Field Mapping'
    _order = "sequence asc"

    import_id = fields.Many2one(
        'google.sheet.importer',
        string='Import',
        required=True,
        ondelete='cascade',
        help="Reference to the Google Sheet import configuration."
    )
    sequence = fields.Integer(
        string='Sequence',
        default=0,
        required=True,
        help="Defines the order of headers in the Google Sheet."
    )
    sheet_header = fields.Char(
        string='Google Sheet Header',
        required=True,
        help="The header name in the Google Sheet."
    )
    mapping_model_id = fields.Many2one(
        related='import_id.mapping_model_id',
        string='Odoo Model',
        readonly=True,
        store=True,
        help="The Odoo model associated with the import configuration."
    )
    odoo_field = fields.Many2one(
        'ir.model.fields',
        string="Odoo Field",
        ondelete='cascade',
        help="The Odoo field that corresponds to the Google Sheet header."
    )
    mandatory = fields.Boolean(
        string='Mandatory Field',
        default=False,
        help="Indicates whether this field is required during import."
    )
    duplicate_check = fields.Boolean(
        string='Check for Duplicates',
        default=False,
        help="If enabled, skips importing records where this field's value already exists in Odoo."
    )

    _sql_constraints = [
        (
            'unique_sheet_header_per_import',
            'unique(import_id, sheet_header)',
            'The Google Sheet Header must be unique within the same import configuration!'
        ),
        (
            'unique_odoo_field_per_import',
            'unique(import_id, odoo_field)',
            'The Odoo Field must be unique within the same import configuration!'
        ),
    ]

    @api.constrains('odoo_field', 'mapping_model_id')
    def _check_odoo_field_model(self):
        """
        Ensures that the selected Odoo field belongs to the model specified
        in the associated import configuration.
        """
        for record in self:
            if record.mapping_model_id and record.odoo_field:
                if record.odoo_field.model_id != record.mapping_model_id:
                    raise ValidationError(
                        "The selected Odoo Field '%s' does not belong to the model '%s'." %
                        (record.odoo_field.name, record.mapping_model_id.name)
                    )

from odoo import models, fields

class ContactStage(models.Model):
    _name = "contact.stage"
    _description = ""

    name = fields.Char(required=True)
    description = fields.Html()

    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Contact stage name must be unique'),
    ]

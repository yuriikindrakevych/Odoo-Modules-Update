from odoo import models, fields, api, tools, exceptions, _


class ProductTemplateSupplier(models.Model):
    # Creating VIEW from tables product.template and product.supplierinfo
    _name = "product.template.supplierinfo"
    _description = "VIEW from tables product.template and product.supplierinfo"
    _auto = False  # <- suppress the Odoo from creating a PSQL table automatically

    product_tmpl_id = fields.Integer(string=_("Product Template Id"))
    default_code = fields.Char(string=_("Default Code"))
    name = fields.Char(string=_("Name"))
    category_name = fields.Char(string=_("Category Name"))
    supplier_code = fields.Char(string=_("Product Code"))
    supplier_name = fields.Char(string=_("Product Name"))
    vendor_name = fields.Char(string=_("Vendor Name"))

    def init(self):
        # initialisation of view(sql)
        self.refresh_information()

    def refresh_information(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self._cr.execute("""create or replace view product_template_supplierinfo as (
            select p.id, s.product_tmpl_id, 
                   p.default_code, p.name, c.complete_name as category_name, s.product_code as supplier_code, 
				   concat_ws(' / ', c.name, s.product_name) as supplier_name,
                   r.name as vendor_name, null as inventory_code, null as items_code, null as inventory_description, 
                   null as inventory_article, null as inventory_quantity, null as purchaseorders_income
              from product_template p
              left join product_supplierinfo s on (p.id = s.product_tmpl_id)
			  left join product_category c on (c.id = p.categ_id)
              left join res_partner r on (r.id = s.partner_id)
             where p.detailed_type = 'product'
        )""")

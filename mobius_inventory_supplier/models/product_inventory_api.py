from odoo import models, fields, api, tools, exceptions, _
from requests.auth import HTTPBasicAuth
from datetime import datetime
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class ApiInventory(models.Model):
    # Information from API (inventory part)
    _name = "api.inventory"
    _description = "Information from API (sync with aclima)"

    code = fields.Char(string=_("Inventory"))
    description = fields.Char(string=_("Description"))
    item_code = fields.Char(string=_("Inventory Item Code"))
    item_description = fields.Text(string=_("Inventory Item Description"))
    item_article = fields.Char(string=_("Inventory Item Article"))
    item_quantity = fields.Integer(string=_("Inventory Item Quantity"))


class ApiPurchaseOrders(models.Model):
    # Information from API (purchaseorders part)
    _name = "api.purchase.orders"
    _description = "Information from API (sync with aclima)"

    code = fields.Char(string=_("PurchaseOrders Code"))
    description = fields.Text(string=_("PurchaseOrders Description"))
    item_code = fields.Char(string=_("PurchaseOrders Item Code"))
    item_description = fields.Text(string=_("PurchaseOrders Item Description"))
    item_article = fields.Char(string=_("PurchaseOrders Item Article"))
    item_income = fields.Text(string=_("PurchaseOrders Item Income"))


class ProductInventoryAPI(models.Model):
    # Information from API
    _name = "product.inventory.api"
    _description = "Information from API (sync with aclima)"

    code = fields.Char(string=_("code"))
    inventory = fields.Char(string=_("Inventory"))
    inventory_code = fields.Char(string=_("Inventory Code"))
    inventory_description = fields.Text(string=_("Inventory Description"))
    inventory_article = fields.Char(string=_("Inventory Article"))
    inventory_quantity = fields.Integer(string=_("Inventory Quantity"),)
    purchaseorders_income = fields.Text(string=_("Inventory Income"))

    def init(self):
        self.refresh_information_api()

    def refresh_information_api(self):
        def get_income(orders_list: list = None):
            income = ""
            try:
                for purchase in orders_list:
                    purchase_date = datetime.fromisoformat(purchase["PurchaseDate"])
                    income += _("Income: %s Quantity: %d; \n") % (
                                f"{purchase_date.year:04}-{purchase_date.month:02}-{purchase_date.day:02}",
                                purchase["Quantity"])
            except Exception as ex:
                _logger.error("Exception (refresh_information_api -> get_income): ", ex)
            return income

        json_data = self._request_information_from_aclima()
        if json_data:
            # truncate api_inventory (delete all records)
            self._cr.execute("""delete from api_inventory""")

            # truncate api_purchase_orders (delete all records)
            self._cr.execute("""delete from api_purchase_orders""")

            vals_inventory = []
            # parsing of the information from the json response (inventory part)
            for rec in json_data["inventory"]:
                for item in rec["Items"]:
                    vals_inventory.append({
                        "code": rec["Code"].strip(),
                        "description": rec["Description"],
                        "item_code": item["Code"].strip(),
                        "item_description": item["Description"],
                        "item_article": item["Article"].strip(),
                        "item_quantity": item["Quantity"],
                    })
            # fill view with information from json(api)
            if vals_inventory:
                self.env["api.inventory"].create(vals_inventory)

            vals_purchaseorders = []
            # parsing of the information from the json response (purchaseorders part)
            for rec in json_data["purchaseorders"]:
                for item in rec["Items"]:
                    vals_purchaseorders.append({
                        "code": rec["Code"].strip(),
                        "description": rec["Description"],
                        "item_code": item["Code"].strip(),
                        "item_description": item["Description"],
                        "item_article": item["Article"].strip(),
                        "item_income": get_income(item["PurchaseDates"])
                    })
            # fill view with information from json(api)
            if vals_purchaseorders:
                self.env["api.purchase.orders"].create(vals_purchaseorders)

            # truncate inventory_supplier (delete all records)
            record_set = self.search([])
            record_set.unlink()

            # truncate product_inventory_api (delete all records)
            self._cr.execute("""delete from product_inventory_api""")

            sql_query = """select
                       coalesce(a.code, p.code) as code, 
                       coalesce(a.description, p.description) as inventory,
                       coalesce(a.item_code, p.item_code) as inventory_code, 
                       coalesce(a.item_description, p.item_description) as inventory_description, 
                       coalesce(a.item_article, p.item_article) as inventory_article, 
                       a.item_quantity as  inventory_quantity, 
                       p.item_income as purchaseorders_income
                  from api_inventory a
                  full join api_purchase_orders p on (p.item_code = a.item_code)
            """
            self._cr.execute(sql_query)

            vals = self._cr.dictfetchall()
            if vals:
                self.env["product.inventory.api"].create(vals)

            return True
        else:
            return False

    def _request_information_from_aclima(self):
        url_from_settings = self.env["ir.config_parameter"].sudo().get_param("aclima_API_URL")
        login_from_settings = self.env["ir.config_parameter"].sudo().get_param("aclima_API_login")
        password_from_settings = self.env["ir.config_parameter"].sudo().get_param("aclima_API_password")

        if not url_from_settings or not login_from_settings or not password_from_settings:
            _logger.error("Error (inventory_supplier -> settings): ")
            return {}

        response_dist = {}
        try:
            with requests.get(url=url_from_settings, auth=HTTPBasicAuth(login_from_settings, password_from_settings)) as response:
                if response.status_code == requests.codes.ok:
                    response_dist = json.loads(response.text)
        except Exception as ex:
            _logger.error("Exception (inventory_supplier -> requests): ", ex)
        return response_dist

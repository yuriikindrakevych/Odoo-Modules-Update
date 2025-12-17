from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers import main
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class MobiusWebsiteSaleDelivery(main.WebsiteSale):

    @http.route("/shop/payment", type="http", auth="public", website=True, sitemap=False)
    def shop_payment(self, **post):
        _logger.info("MobiusWebsiteSaleDelivery.shop_payment")
        return super(MobiusWebsiteSaleDelivery, self).shop_payment(**post)

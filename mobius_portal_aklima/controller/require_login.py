from odoo import http

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.web import Home

class RequireLoginToWebsiteSale(WebsiteSale):

    @http.route(auth="user")
    def checkout(self, **post):
        return super().checkout(**post)

    @http.route(auth="user")
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        return super().shop(
            page=page,
            category=category,
            search=search,
            min_price=min_price,
            max_price=max_price,
            ppg=ppg,
            **post
            )

    @http.route(auth="user")
    def cart(self, **post):
        return super().cart(**post)

class RequireLoginHome(Home):

    @http.route(auth="user")
    def index(self, **kw):
        return super().index(**kw)

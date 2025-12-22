# -*- coding: utf-8 -*-
import logging
import json
import uuid
import time
from collections import OrderedDict

import odoo
from odoo import http
from odoo.addons.web.controllers.home import Home
from odoo.addons.web.controllers.utils import ensure_db
from odoo.http import request
from werkzeug.utils import redirect

_logger = logging.getLogger(__name__)

class AutoLoginHome(Home):

    @http.route("/mobius/auth", type="jsonrpc", auth="none", methods=["POST", "OPTIONS"], csrf=False, website=True, cors="*")
    def auth(self, db, login, password):
        session_id = uuid.uuid1().hex
        request.env["mobius.session"].sudo().create({
            "session_id" : session_id,
            "db_name" : db,
            "login" : login,
            "password" : password,
            })
        _logger.warning("Session ADD, session_id=%s", session_id)
        return session_id

    @http.route("/mobius/enter/<string:session_id>", type="http", auth="none", methods=["GET", "OPTIONS"], csrf=False, website=True, cors="*")
    def enter(self, session_id, *args, **kwargs):
        if request.httprequest.cookies.get("mob_session_id", None) is None:
            _logger.warning("enter: session not found: " + session_id)
        else:
            _logger.warning("enter: session found: " + session_id)
        ret = redirect("/my/home", 303)
        ret.set_cookie("mob_session_id", session_id, max_age=90 * 24 * 60 * 60, httponly=True)
        return ret

    @http.route("/web/login", type="http", auth="none", sitemap=False, csrf=False)
    def web_login(self, redirect=None, **kw):
        try:
            ensure_db()
            session_id = request.httprequest.cookies.get("mob_session_id", None)
            if not session_id:
                _logger.warning("No mob_session_id cookie")
                return super().web_login(redirect=redirect, **kw)
            _logger.warning("Session ID: " + session_id)
            session = request.env["mobius.session"].sudo().search([("session_id", "=", session_id)])
            _logger.warning("Session=%s", session)

            if session is None or not session:
                _logger.warning("Mobius session not found: " + session_id)
                return super().web_login(redirect=redirect, **kw)

            db = session.db_name
            login = session.login
            password = session.password

            session.sudo().unlink()
            uid = request.session.authenticate(db, login, password)
            request.params["login_success"] = True
            request.params["password"] = password
            _logger.warning("UID: " + str(uid))
            ret = request.redirect(self._login_redirect(uid, redirect=redirect))
            _logger.warning("ret: " + str(ret))
            return ret

        except Exception as e:
            _logger.warning("Mobius login failed: " + str(e))
            return super().web_login(redirect=redirect, **kw)

#!/usr/bin/python3
from _thread import _local

from odoo import api, models, fields, tools
from odoo import _
import logging
import json

_logger = logging.getLogger(__name__)


class Lead(models.Model):
    _inherit = "crm.lead"

    @api.model_create_multi
    def create(self, vals_list):
        leads = super(Lead, self.with_context(raise_exception=False)).create(vals_list)
        context = self.env.context
        _logger.info("context=%s", context)
        if context.get("from_API"):
            leads._check_ability_create_portal_user()
        return leads

    def _get_user_by_partner_id(self, partner_id):
        user = self.env["res.users"].search([("partner_id", "=", partner_id.id)], limit=1)
        if user:
            return user
        return False

    def _validate_partner_phone_and_email(self):
        self.ensure_one()
        if not self.partner_id.phone and self.phone:
            self.partner_id.write({"phone": self.phone})
        if not self.partner_id.email and self.email_from:
            self.partner_id.write({"email": self.email_from})

    def _validate_partner_phone(self, partner_id):
        self.ensure_one()
        if not partner_id.phone and self.phone:
            partner_id.write({"phone": self.phone})

    def _create_portal_user(self, partner_id, validate_partner_phone=True):
        self.ensure_one()
        if validate_partner_phone:
            self._validate_partner_phone(partner_id)

        self._create_user_for_api(partner_id)
        self.write({"partner_id": partner_id.id})
    def _check_ability_create_portal_user(self):
        # FIX ME
        """
            Мета: перевірити чи існує контакт (res.partner) за email та створити для нього користувача (res.users) (порта)

            1. Якщо у ліда встановлено partner_id:
                1.1.    Перевіряємо поля контакту phone та email, якщо пусті - записуємо значення з ліда.
                1.2.    Перевіряємо чи існує користувач за цим контактом, якщо ні - створююємо

            2. Шукаємо контакт за email:
                2.0     Якщо не знайдено контакт - переходимо на наступний лід

                2.1     Якщо для контакту існує користувач записуємо цей контакт у лід
                2.1.1   Перевіряємо чи заповнене поле phone у контакті, якщо ні - заповнюємо

                2.2     Якщо знайдено тільки 1 контакт а email - створюємо користувача

                2.3     Якщо є декілька контактів за email - шукаємо за phone та mobile
                2.3.1   Для першого знайденого контакту - створюємо користувача
        """
        ResPartner = self.env["res.partner"]
        ResUsers = self.env["res.users"]
        _logger.info("_check_ability_create_portal_user=%s", self)
        for lead in self:
            if lead.partner_id:
                lead._validate_partner_phone_and_email()

                user = ResUsers.search([("partner_id", "=", lead.partner_id.id)], limit=1)
                if not self._get_user_by_partner_id(lead.partner_id):
                    lead._create_user_for_api(lead.partner_id)
                    continue

            if not lead.email_from:
                continue

            partner_id = ResPartner.search([("email", "=", lead.email_from)])
            if not partner_id:
                continue

            for par in partner_id:
                if self._get_user_by_partner_id(par):
                    lead._validate_partner_phone(partner_id=partner_id)
                    lead.write({"partner_id": partner_id.id})
                    continue

            if len(partner_id) == 1:
                lead._create_portal_user(partner_id=partner_id)
                continue

            if lead.phone or lead.mobile:
                phone = lead.phone if lead.phone else lead.mobile
                phone = ResPartner._phone_format(phone)
                domain = [
                    ("email", "=", lead.email_from),
                    "|",
                        ("phone", "=", phone),
                        ("mobile", "=", phone)
                ]
                partner_mixed_id = ResPartner.search(domain, order="phone")
                if partner_mixed_id:
                    lead._create_portal_user(partner_id=partner_mixed_id[0])
                    continue
            lead._create_portal_user(partner_id=partner_id[0])
            continue


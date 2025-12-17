from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = "res.users"

    @api.model
    def change_password(self, old_passwd, new_passwd):
        result = super().change_password(old_passwd, new_passwd)
        if self.env.user.partner_id:
            self.env.user.partner_id.write({"techinal_password": new_passwd})
            _logger.info("Technical password change for '%s' (#%s)", self.env.user.login, self.env.uid)
        return result


class ChangePasswordUser(models.TransientModel):
    _inherit = "change.password.user"

    def change_password_button(self):
        for line in self:
            if line.new_passwd and line.user_id.partner_id:
                line.user_id.partner_id.write({"techinal_password": line.new_passwd})
                _logger.info("Technical password change for '%s'", line.user_login)
        result = super().change_password_button()
        return result

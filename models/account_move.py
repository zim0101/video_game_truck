from odoo import models
from ..twilio_sms.sms import send_sms


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        print('Custom action_post method in custom_sales_log called')
        res = super(AccountMove, self).action_post()
        print('Account Move {} has been posted.'.format(res))
        return res

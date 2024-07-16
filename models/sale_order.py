import logging
from datetime import datetime, timedelta
from odoo import fields, models, api
from pprint import pformat
from ..twilio_sms.sms import send_sms

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    booking_date = fields.Date(string='Booking Date')
    booking_time = fields.Float(string='Booking Time')
    booking_end = fields.Float(string='Booking End')

    booking_datetime_start = fields.Datetime(string='Booking Datetime Start', compute='_compute_booking_datetime',
                                             store=True)
    booking_datetime_end = fields.Datetime(string='Booking Datetime End', compute='_compute_booking_datetime',
                                           store=True)

    @api.depends('booking_date', 'booking_time', 'booking_end')
    def _compute_booking_datetime(self):
        for order in self:
            if order.booking_date and order.booking_time is not None and order.booking_end is not None:
                booking_datetime = datetime.combine(order.booking_date, datetime.min.time())
                start_time = int(order.booking_time * 60 * 60)
                end_time = int(order.booking_end * 60 * 60)
                order.booking_datetime_start = booking_datetime + timedelta(seconds=start_time)
                order.booking_datetime_end = booking_datetime + timedelta(seconds=end_time)

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        send_sms('Your order is canceled.')

        return res

    def _create_invoices(self, grouped=False, final=False):
        res = super(SaleOrder, self)._create_invoices(grouped=grouped, final=final)
        send_sms('Your order is confirmed.')
        send_sms("You have a sale order at {}. From {} to {}".format(self.booking_date,
                                                                     self.booking_datetime_start,
                                                                     self.booking_datetime_end))

        return res


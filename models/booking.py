from odoo import models, fields, api
from datetime import datetime


class Booking(models.Model):
    _name = 'video_game_truck.booking'
    _description = 'Video Game Truck Booking'

    name = fields.Char(string='Booking Name', required=True, compute='_compute_name')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', ondelete='set null')
    product_template_id = fields.Many2one('product.template', string='Product', ondelete='set null')
    slot_id = fields.Many2one('video_game_truck.slot', string='Slot', ondelete='set null')
    video_game_truck_ids = fields.One2many('video_game_truck.truck', 'booking_id',
                                           string='Video Game Trucks')
    booking_datetime_start = fields.Datetime(string='Booking Datetime Start', compute='_compute_booking_datetime',
                                             store=True)
    booking_datetime_end = fields.Datetime(string='Booking Datetime End', compute='_compute_booking_datetime',
                                           store=True)

    @api.depends('slot_id')
    def _compute_booking_datetime(self):
        for record in self:
            if record.slot_id:
                now = datetime.now()

                slot_start_time = datetime(year=now.year, month=now.month, day=now.day,
                                           hour=int(record.slot_id.start_time))
                slot_end_time = datetime(year=now.year, month=now.month, day=now.day,
                                         hour=int(record.slot_id.end_time))

                record.booking_datetime_start = slot_start_time
                record.booking_datetime_end = slot_end_time
            else:
                record.booking_datetime_start = False
                record.booking_datetime_end = False

    @api.depends('sale_order_id')
    def _compute_name(self):
        for booking in self:
            booking.name = booking.product_template_id.name + ' - ' + booking.sale_order_id.name




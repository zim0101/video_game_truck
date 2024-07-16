from odoo import models, fields, api
from datetime import datetime


class Booking(models.Model):
    _name = 'video_game_truck.booking'
    _description = 'Video Game Truck Booking'

    name = fields.Char(string='Booking Name', required=True, compute='_compute_name')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', ondelete='set null')
    product_template_id = fields.Many2one('product.template', string='Product', ondelete='set null')
    slot_id = fields.Many2one('video_game_truck.slot', string='Slot', ondelete='set null')
    video_game_truck_ids = fields.Many2many('video_game_truck.truck', 'video_game_truck_booking_truck_rel',
                                            'booking_id', 'truck_id', string='Assigned Video Game Trucks',
                                            domain="[('id', 'in', available_truck_ids)]")  # Updated domain
    available_truck_ids = fields.Many2many('video_game_truck.truck', compute='_compute_available_trucks')

    booking_date = fields.Date(string='Booking Date')
    booking_datetime_start = fields.Datetime(string='Booking Datetime Start', compute='_compute_booking_datetime',
                                             store=True)
    booking_datetime_end = fields.Datetime(string='Booking Datetime End', compute='_compute_booking_datetime',
                                           store=True)
    number_of_trucks_ordered = fields.Integer(string='Number of Trucks Ordered')

    @api.depends('product_template_id', 'booking_date', 'slot_id')
    def _compute_available_trucks(self):
        for record in self:
            if record.product_template_id and record.booking_date and record.slot_id:
                bookings = self.env['video_game_truck.booking'].search([
                    ('slot_id', '=', record.slot_id.id),
                    ('booking_date', '=', record.booking_date),
                    ('id', '!=', record.id),
                ])
                print(bookings.ids, record.id)
                available_trucks = self.env['video_game_truck.truck'].search([
                    ('product_id', '=', record.product_template_id.id),
                    ('id', 'not in', bookings.mapped('video_game_truck_ids').ids),
                ])
                record.available_truck_ids = available_trucks
            else:
                record.available_truck_ids = False

    @api.depends('sale_order_id')
    def _compute_name(self):
        for booking in self:
            booking.name = booking.product_template_id.name + ' - ' + booking.sale_order_id.name

    @api.onchange('product_template_id', 'booking_date', 'slot_id')
    def _onchange_product_or_date(self):
        self.video_game_truck_ids = False  # Reset trucks to enforce domain update

    @api.depends('slot_id', 'booking_date')
    def _compute_booking_datetime(self):
        for record in self:
            if record.slot_id:
                slot_start_time = datetime(year=record.booking_date.year, month=record.booking_date.month, day=record.booking_date.day,
                                           hour=int(record.slot_id.start_time_float))
                slot_end_time = datetime(year=record.booking_date.year, month=record.booking_date.month, day=record.booking_date.day,
                                         hour=int(record.slot_id.end_time_float))

                record.booking_datetime_start = slot_start_time
                record.booking_datetime_end = slot_end_time
            else:
                record.booking_datetime_start = False
                record.booking_datetime_end = False

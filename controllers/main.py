import json
import logging
from datetime import datetime
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class MainControllers(http.Controller):

    @http.route('/', type='http', auth="public")
    def home(self, **kwargs):
        return request.redirect('/service_pricing')

    @http.route('/buy_now/<string:product_template_id>', type='http', auth="public", website=True, methods=['POST'])
    def buy_now(self, product_template_id, **kwargs):
        booking_date = kwargs.get('booking_date')
        booking_time = kwargs.get('booking_time')
        number_of_trucks = kwargs.get('number_of_trucks')

        if not booking_date or not booking_time:
            _logger.error("Booking date or time not provided")
            return request.redirect('/service_pricing?error=Booking%20date%20or%20time%20not%20provided')

        try:
            hours, minutes = map(int, booking_time.split(':'))
            booking_time_float = hours + minutes / 60.0
        except ValueError:
            _logger.error("Invalid booking time format: %s", booking_time)
            return request.redirect('/service_pricing?error=Invalid%20booking%20time%20format')

        booking_end_float = booking_time_float + 4.0

        overlapping_orders = request.env['sale.order'].sudo().search([
            ('booking_date', '=', booking_date),
            '|',
            '&', ('booking_time', '<=', booking_time_float), ('booking_end', '>=', booking_time_float),
            '&', ('booking_time', '<=', booking_end_float), ('booking_end', '>=', booking_end_float),
        ])

        if overlapping_orders:
            _logger.error("Booking slot overlaps with existing orders")
            return request.redirect('/service_pricing?error=Booking%20slot%20is%20not%20available')

        product_template = http.request.env['product.template'].search(
            [
                ('id', '=', int(product_template_id)),
                ('type', '=', 'service')
            ], limit=1
        )

        if not product_template:
            _logger.error("Product template not found: %s", product_template_id)
            return request.redirect('/service_pricing?error=Product%20template%20not%20found')

        product = product_template.product_variant_id

        if not product:
            _logger.error("No product variant found for template: %s", product_template_id)
            return request.redirect('/service_pricing?error=No%20product%20variant%20found%20for%20template')

        order = request.website.sale_get_order(force_create=True)

        if order:
            order.order_line.unlink()

        order._cart_update(product_id=product.id, add_qty=1, set_qty=1)
        order.booking_date = booking_date
        order.booking_time = booking_time_float

        checkout_url = '/shop/checkout'

        return request.redirect(checkout_url)

    @http.route('/service_pricing', type='http', auth="public", website=True)
    def pricing_page(self, **kwargs):
        products = http.request.env['product.template'].sudo().search(
            [
                ('sale_ok', '=', True),
                ('purchase_ok', '=', True),
                ('type', '=', 'service')
            ],
            order='list_price asc'
        )

        return request.render('video_game_truck.pricing_page_template', {'products': products})

    @http.route('/fetch_available_slots', type='http', auth='public')
    def fetch_available_slots(self, **kwargs):
        product_id = kwargs.get('product_id')
        booking_date = kwargs.get('booking_date')
        number_of_trucks = kwargs.get('number_of_trucks')

        print(product_id, booking_date, number_of_trucks)

        if product_id is None or booking_date is None or number_of_trucks is None:
            return '{"error": "Missing required parameters"}'

        available_slots = []
        booking_date = datetime.strptime(booking_date, '%Y-%m-%d')
        slots = request.env['video_game_truck.slot'].sudo().search([])
        product = http.request.env['product.template'].sudo().search(
            [
                ('id', '=', int(product_id)),
                ('type', '=', 'service')
            ], limit=1
        )

        for slot in slots:
            bookings = request.env['video_game_truck.booking'].sudo().search([
                ('product_template_id', '=', product_id),
                ('booking_datetime_start', '=', booking_date),
                ('slot_id', '=', slot.id)
            ])

            if bookings:
                for booking in bookings:
                    if (len(product.video_game_truck_ids) - len(booking.video_game_truck_ids)) <= number_of_trucks:
                        available_slot = {
                            "id": slot.id,
                            "name": slot.name,
                            "start_time": slot.start_time,
                            "end_time": slot.end_time
                        }
                        available_slots.append(available_slot)
            else:
                available_slot = {
                    "id": slot.id,
                    "name": slot.name,
                    "start_time": slot.start_time,
                    "end_time": slot.end_time
                }
                available_slots.append(available_slot)

        # Serialize available_slots to JSON before returning
        return json.dumps(available_slots)



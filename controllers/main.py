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
        number_of_trucks = kwargs.get('number_of_trucks')
        slot_id = kwargs.get('slot')

        if not slot_id:
            _logger.error("Slot not provided")
            return request.redirect('/service_pricing?error=Slot%20not%20provided')

        slot = request.env['video_game_truck.slot'].sudo().browse(int(slot_id))

        product_template = request.env['product.template'].sudo().search(
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

        booking_vals = {
            'product_template_id': product_template.id,
            'slot_id': slot.id,
            'sale_order_id': order.id,
            'number_of_trucks_ordered': number_of_trucks,
            'booking_date': booking_date,
        }

        request.env['video_game_truck.booking'].sudo().create(booking_vals)

        # Update the order with booking information
        order._cart_update(product_id=product.id, add_qty=1, set_qty=1)
        order.booking_date = booking_date
        order.booking_time = slot.start_time_float
        order.booking_end = slot.end_time_float

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
        available_slots = []

        product_id = kwargs.get('product_id')
        booking_date = kwargs.get('booking_date')
        number_of_trucks_requested = int(kwargs.get('number_of_trucks'))

        if product_id is None or booking_date is None or number_of_trucks_requested is None:
            return '{"error": "Missing required parameters"}'

        booking_date = datetime.strptime(booking_date, '%Y-%m-%d').date()

        slots = request.env['video_game_truck.slot'].sudo().search([])

        product = http.request.env['product.template'].sudo().search(
            [
                ('id', '=', int(product_id)),
                ('type', '=', 'service')
            ], limit=1
        )

        for slot in slots:
            existing_bookings = request.env['video_game_truck.booking'].sudo().search(
                [
                    ('product_template_id', '=', product.id),
                    ('booking_date', '=', booking_date),
                    ('slot_id', '=', slot.id)
                ]
            )

            if existing_bookings:
                trucks_in_use = 0

                for booking in existing_bookings:
                    trucks_in_use += booking.number_of_trucks_ordered

                available_trucks = len(product.video_game_truck_ids) - trucks_in_use

                if available_trucks >= number_of_trucks_requested:
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

        return json.dumps(available_slots)

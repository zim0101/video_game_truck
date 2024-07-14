from odoo import fields, models, api


class VideoGameTruck(models.Model):
    _name = 'video_game_truck.truck'
    _description = 'Video Game Truck'

    name = fields.Char(string='Truck Name', required=True)
    truck_id_number = fields.Char(string='Truck ID Number', required=True)
    number_of_seats = fields.Integer(string='Number of Seats', required=True)
    product_id = fields.Many2one('product.template', string='Product', ondelete='set null')
    booking_id = fields.Many2one('video_game_truck.booking', string='Booking')

    _sql_constraints = [
        ('truck_id_number_unique',
         'UNIQUE(truck_id_number)',
         'The truck ID number must be unique!')
    ]

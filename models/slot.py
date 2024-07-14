from odoo import models, fields


class Slot(models.Model):
    _name = 'video_game_truck.slot'
    _description = 'Time Slots'

    name = fields.Char(string='Name', required=True)
    start_time = fields.Float(string='Start Time', required=True, help="Start time in hours (e.g., 9.5 for 9:30 AM)")
    end_time = fields.Float(string='End Time', required=True, help="End time in hours (e.g., 17 for 5:00 PM)")

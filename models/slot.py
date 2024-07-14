from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class Slot(models.Model):
    _name = 'video_game_truck.slot'
    _description = 'Slot'

    name = fields.Char(string='Name', required=True)
    start_time = fields.Float(string='Start Time', required=True, help="Start time in hours (e.g., 9.5 for 9:30 AM)")
    end_time = fields.Float(string='End Time', required=True, help="End time in hours (e.g., 17 for 5:00 PM)")

    @api.constrains('start_time', 'end_time')
    def _check_overlap(self):
        for record in self:
            if record.end_time <= record.start_time:
                raise ValidationError("Slot end time cannot be before or the same as start time.")

            domain = [
                ('id', '!=', record.id),
                ('start_time', '<', record.end_time),
                ('end_time', '>', record.start_time),
            ]
            overlaps = self.search(domain)
            if overlaps:
                raise ValidationError(
                    f"Slot '{record.name}' overlaps with existing slots: {', '.join(overlaps.mapped('name'))}"
                )

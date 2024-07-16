from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Slot(models.Model):
    _name = 'video_game_truck.slot'
    _description = 'Time Slots'

    name = fields.Char(string='Name', required=True)
    start_time = fields.Selection(
        string="Start Time",
        selection=lambda self: self._get_time_options(),
        required=True
    )
    end_time = fields.Selection(
        string="End Time",
        selection=lambda self: self._get_time_options(),
        required=True
    )

    start_time_float = fields.Float(string="Stored Start Time", compute="_compute_start_time_float", store=True)
    end_time_float = fields.Float(string="Stored End Time", compute="_compute_end_time_float", store=True)


    @api.depends('start_time')
    def _compute_start_time_float(self):
        for record in self:
            print(record.start_time)
            hour = int(record.start_time.split(':')[0])
            minute = int(record.start_time.split(':')[1].split(' ')[0])
            is_am_or_pm = record.start_time.split(':')[1].split(' ')[1]
            if is_am_or_pm == "PM" and hour != 12:
                hour += 12
            elif is_am_or_pm == "AM" and hour == 12:
                hour = 0
            record.start_time_float = float(hour) + float(minute) / 60
            print(record.start_time_float)

    @api.depends('end_time')
    def _compute_end_time_float(self):
        for record in self:
            hour = int(record.end_time.split(':')[0])
            minute = int(record.end_time.split(':')[1].split(' ')[0])
            is_am_or_pm = record.end_time.split(':')[1].split(' ')[1]
            if is_am_or_pm == "PM" and hour != 12:
                hour += 12
            elif is_am_or_pm == "AM" and hour == 12:
                hour = 0
            record.end_time_float = float(hour) + float(minute) / 60
            print(record.end_time_float)

    @api.model
    def _get_time_options(self):
        working_time = self.env['video_game_truck.working_time'].search([], limit=1)
        return working_time.get_slot_time_options(working_time) if working_time else []

    @api.constrains('start_time_float', 'end_time_float')
    def _check_time_order(self):
        for record in self:
            print(self.start_time_float, self.end_time_float)
            if record.start_time_float >= record.end_time_float:
                raise ValidationError("Start time must be before end time.")

    @api.constrains('start_time_float', 'end_time_float')
    def _check_time_conflict(self):
        for record in self:
            conflicting_slots = self.search([
                ('id', '!=', record.id),
                ('start_time_float', '<', record.end_time_float),
                ('end_time_float', '>', record.start_time_float),
            ])
            if conflicting_slots:
                raise ValidationError("Time slots cannot conflict with existing slots.")

    @api.model
    def _check_bookings_exist(self):
        for slot in self:
            bookings = self.env['video_game_truck.booking'].search([
                ('slot_id', '=', slot.id),
                ('booking_datetime_end', '>=', fields.Datetime.now()),
            ])
            if bookings:
                raise ValidationError("Cannot update slot because there are future bookings in that slot.")

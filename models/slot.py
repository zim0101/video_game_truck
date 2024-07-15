from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Slot(models.Model):
    _name = 'video_game_truck.slot'
    _description = 'Time Slots'

    name = fields.Char(string='Name', required=True)
    start_time = fields.Selection(
        [
            ("12:00", "12:00"),
            ("01:00", "01:00"),
            ("02:00", "02:00"),
            ("03:00", "03:00"),
            ("04:00", "04:00"),
            ("05:00", "05:00"),
            ("06:00", "06:00"),
            ("07:00", "07:00"),
            ("08:00", "08:00"),
            ("09:00", "09:00"),
            ("10:00", "10:00"),
            ("11:00", "11:00"),
        ],
        string="Start Time", required=True
    )
    is_start_time_am = fields.Boolean(string="AM", default=False)
    is_start_time_pm = fields.Boolean(string="PM", default=True)

    end_time = fields.Selection(
        [
            ("12:00", "12:00"),
            ("01:00", "01:00"),
            ("02:00", "02:00"),
            ("03:00", "03:00"),
            ("04:00", "04:00"),
            ("05:00", "05:00"),
            ("06:00", "06:00"),
            ("07:00", "07:00"),
            ("08:00", "08:00"),
            ("09:00", "09:00"),
            ("10:00", "10:00"),
            ("11:00", "11:00"),
        ],
        string="End Time", required=True
    )
    is_end_time_am = fields.Boolean(string="AM", default=False)
    is_end_time_pm = fields.Boolean(string="PM", default=True)

    start_time_float = fields.Float(string="Stored Start Time", compute="_compute_start_time_float", store=True)
    end_time_float = fields.Float(string="Stored End Time", compute="_compute_end_time_float", store=True)

    start_time_display = fields.Char(string="Display Start Time", compute="_compute_start_time_display")
    end_time_display = fields.Char(string="Display End Time", compute="_compute_end_time_display")

    @api.depends('start_time', 'is_start_time_am', 'is_start_time_pm')
    def _compute_start_time_float(self):
        for record in self:
            hour = int(record.start_time.split(':')[0])
            if record.is_start_time_pm and hour != 12:
                hour += 12
            elif record.is_start_time_am and hour == 12:
                hour = 0
            record.start_time_float = float(hour)

    @api.depends('end_time', 'is_end_time_am', 'is_end_time_pm')
    def _compute_end_time_float(self):
        for record in self:
            hour = int(record.end_time.split(':')[0])
            if record.is_end_time_pm and hour != 12:
                hour += 12
            elif record.is_end_time_am and hour == 12:
                hour = 0
            record.end_time_float = float(hour)

    @api.depends('start_time_float')
    def _compute_start_time_display(self):
        for record in self:
            hour = int(record.start_time_float)
            am_pm = 'AM' if hour < 12 else 'PM'
            if hour > 12:
                hour -= 12
            elif hour == 0:
                hour = 12
            record.start_time_display = f"{hour}:00 {am_pm}"

    @api.depends('end_time_float')
    def _compute_end_time_display(self):
        for record in self:
            hour = int(record.end_time_float)
            am_pm = 'AM' if hour < 12 else 'PM'
            if hour > 12:
                hour -= 12
            elif hour == 0:
                hour = 12
            record.end_time_display = f"{hour}:00 {am_pm}"

    @api.onchange('is_start_time_am')
    def _onchange_is_start_time_am(self):
        if self.is_start_time_am:
            self.is_start_time_pm = False

    @api.onchange('is_start_time_pm')
    def _onchange_is_start_time_pm(self):
        if self.is_start_time_pm:
            self.is_start_time_am = False

    @api.onchange('is_end_time_am')
    def _onchange_is_end_time_am(self):
        if self.is_end_time_am:
            self.is_end_time_pm = False

    @api.onchange('is_end_time_pm')
    def _onchange_is_end_time_pm(self):
        if self.is_end_time_pm:
            self.is_end_time_am = False

    @api.constrains('start_time_float', 'end_time_float')
    def _check_time_order(self):
        for record in self:
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

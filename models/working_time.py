from odoo import models, fields, api
from odoo.exceptions import ValidationError

class WorkingTime(models.Model):
    _name = 'video_game_truck.working_time'
    _description = 'Working Time'

    name = fields.Char(string='Name', required=True)
    start_time = fields.Selection(
        string="Start Time",
        selection='_get_working_time_options',
        required=True
    )
    end_time = fields.Selection(
        string="End Time",
        selection='_get_working_time_options',
        required=True
    )

    is_start_time_am = fields.Boolean(string="AM", default=False)
    is_start_time_pm = fields.Boolean(string="PM", default=True)
    is_end_time_am = fields.Boolean(string="AM", default=False)
    is_end_time_pm = fields.Boolean(string="PM", default=True)

    start_time_float = fields.Float(string="Stored Start Time", compute="_compute_start_time_float", store=True)
    end_time_float = fields.Float(string="Stored End Time", compute="_compute_end_time_float", store=True)

    start_time_display = fields.Char(string="Display Start Time", compute="_compute_start_time_display")
    end_time_display = fields.Char(string="Display End Time", compute="_compute_end_time_display")

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

    @api.model
    def create(self, vals):
        if self.search_count([]) > 0:
            raise ValidationError("Only one working time entry is allowed.")
        return super(WorkingTime, self).create(vals)

    def write(self, vals):
        if self.search_count([('id', '!=', self.id)]) > 0:
            raise ValidationError("Only one working time entry is allowed.")
        return super(WorkingTime, self).write(vals)

    @api.model
    def _check_bookings_exist(self, vals):
        for working_time in self:
            bookings = self.env['video_game_truck.booking'].search([
                ('slot_id.start_time_float', '>=', working_time.start_time_float),
                ('slot_id.end_time_float', '<=', working_time.end_time_float),
                ('booking_datetime_end', '>=', fields.Datetime.now()),
            ])
            if bookings:
                raise ValidationError("Cannot update working time because there are future bookings.")
        return super(WorkingTime, self).create(vals)

    @api.model
    def _get_working_time_options(self):
        time_options = []
        current_time = 1
        while current_time < 12.5:
            hour = int(current_time)
            minute = int((current_time - hour) * 60)
            time_string = f"{hour:02d}:{minute:02d}"
            time_options.append((time_string, time_string))
            current_time += 0.5  # 30-minute intervals
        return time_options

    @staticmethod
    def get_slot_time_options(self):
        time_options = []
        start_hour = int(self.start_time.split(':')[0])
        start_minute = int(self.start_time.split(':')[1])

        if self.is_start_time_pm and start_hour != 12:
            start_hour += 12
        elif self.is_start_time_am and start_hour == 12:
            start_hour = 0

        # Convert hour and minute into a floating-point representation
        start_time = float(start_hour) + float(start_minute) / 60

        end_hour = int(self.end_time.split(':')[0])
        end_minute = int(self.end_time.split(':')[1])

        if self.is_end_time_pm and end_hour != 12:
            end_hour += 12
        elif self.is_end_time_am and end_hour == 12:
            end_hour = 0

        # Convert hour and minute into a floating-point representation
        end_time = float(end_hour) + float(end_minute) / 60

        while start_time < end_time:

            hour = int(start_time)
            minute = int((start_time - hour) * 60)
            if hour < 12:
                time_string = f"{hour:02d}:{minute:02d}"+" AM"
            else:
                time_string = f"{(12 if hour==12 else hour-12):02d}:{minute:02d}"+" PM"
            time_options.append((time_string, time_string))
            start_time += 1  # 30-minute intervals
        return time_options

    @api.depends('start_time', 'is_start_time_am', 'is_start_time_pm')
    def _compute_start_time_float(self):
        for record in self:
            hour = int(record.start_time.split(':')[0])
            minute = int(record.start_time.split(':')[1])

            if record.is_start_time_pm and hour != 12:
                hour += 12
            elif record.is_start_time_am and hour == 12:
                hour = 0

            # Convert hour and minute into a floating-point representation
            record.start_time_float = float(hour) + float(minute) / 60

    @api.depends('end_time', 'is_end_time_am', 'is_end_time_pm')
    def _compute_end_time_float(self):
        for record in self:
            hour = int(record.end_time.split(':')[0])
            minute = int(record.end_time.split(':')[1])

            if record.is_end_time_pm and hour != 12:
                hour += 12
            elif record.is_end_time_am and hour == 12:
                hour = 0

            # Convert hour and minute into a floating-point representation
            record.end_time_float = float(hour) + float(minute) / 60

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

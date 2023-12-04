import calendar
import datetime
import pytz
import time

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class GenerateSession(models.TransientModel):
	_name = "generate.time.table"
	_description = "Generate Sessions"
	_rec_name = "standard_id"

	standard_id = fields.Many2one('student.class', string='Standard', required=True)
	division_id = fields.Many2one('student.division', string='Division', required=True)
	time_table_lines = fields.One2many(
		'gen.time.table.line', 'gen_time_table')
	time_table_lines_1 = fields.One2many(
		'gen.time.table.line', 'gen_time_table', domain=[('day', '=', '0')])
	time_table_lines_2 = fields.One2many(
		'gen.time.table.line', 'gen_time_table', domain=[('day', '=', '1')])
	time_table_lines_3 = fields.One2many(
		'gen.time.table.line', 'gen_time_table', domain=[('day', '=', '2')])
	time_table_lines_4 = fields.One2many(
		'gen.time.table.line', 'gen_time_table', domain=[('day', '=', '3')])
	time_table_lines_5 = fields.One2many(
		'gen.time.table.line', 'gen_time_table', domain=[('day', '=', '4')])
	time_table_lines_6 = fields.One2many(
		'gen.time.table.line', 'gen_time_table', domain=[('day', '=', '5')])
	time_table_lines_7 = fields.One2many(
		'gen.time.table.line', 'gen_time_table', domain=[('day', '=', '6')])
	start_date = fields.Date(
		string='Start Date', required=True, default=time.strftime('%Y-%m-01'))
	end_date = fields.Date(string='End Date', required=True)

	@api.constrains('start_date', 'end_date')
	def check_dates(self):
		start_date = fields.Date.from_string(self.start_date)
		end_date = fields.Date.from_string(self.end_date)
		if start_date > end_date:
			raise ValidationError(_("End Date cannot be set before Start Date."))

	@api.onchange('standard_id')
	def onchange_standard(self):
		if self.division_id and self.standard_id:
			if self.division_id.standard_id != self.standard_id:
				self.division_id = False

	def act_gen_time_table(self):
		session_obj = self.env['student.timetable']
		for session in self:
			start_date = session.start_date
			end_date = session.end_date
			for n in range((end_date - start_date).days + 1):
				curr_date = start_date + datetime.timedelta(n)
				for line in session.time_table_lines:
					if int(line.day) == curr_date.weekday():
						hour = line.timing_id.hour
						if line.timing_id.am_pm == 'pm' and int(hour) != 12:
							hour = int(hour) + 12
						per_time = '%s:%s:00' % (hour, line.timing_id.minute)
						final_date = datetime.datetime.strptime(
							curr_date.strftime('%Y-%m-%d ') +
							per_time, '%Y-%m-%d %H:%M:%S')
						local_tz = pytz.timezone(
							self.env.user.partner_id.tz or 'GMT')
						local_dt = local_tz.localize(final_date, is_dst=None)
						utc_dt = local_dt.astimezone(pytz.utc)
						utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
						curr_start_date = datetime.datetime.strptime(
							utc_dt, "%Y-%m-%d %H:%M:%S")
						curr_end_date = curr_start_date + datetime.timedelta(
							hours=line.timing_id.duration)
						session_obj.create({
							'teacher_id': line.teacher_id.id,
							'subject_id': line.subject_id.id,
							'standard_id': session.standard_id.id,
							'division_id': session.division_id.id,
							'timing_id': line.timing_id.id,
							'classroom_id': line.classroom_id.id,
							'start_time':
							curr_start_date.strftime("%Y-%m-%d %H:%M:%S"),
							'end_time':
							curr_end_date.strftime("%Y-%m-%d %H:%M:%S"),
							'type': calendar.day_name[int(line.day)],
						})
			return {'type': 'ir.actions.act_window_close'}


class GenerateSessionLine(models.TransientModel):
	_name = 'gen.time.table.line'
	_description = 'Generate Time Table Lines'
	_rec_name = 'day'

	gen_time_table = fields.Many2one(
		'generate.time.table', string='Time Table', required=True)
	teacher_id = fields.Many2one('student.teacher', string='Teacher', required=True)
	subject_id = fields.Many2one('student.subject', string='Subject', required=True)
	timing_id = fields.Many2one('student.timing', string='Timing', required=True)
	classroom_id = fields.Many2one('student.classroom', string='Classroom')
	day = fields.Selection([
		('0', calendar.day_name[0]),
		('1', calendar.day_name[1]),
		('2', calendar.day_name[2]),
		('3', calendar.day_name[3]),
		('4', calendar.day_name[4]),
		('5', calendar.day_name[5]),
		('6', calendar.day_name[6]),
	], string='Day', required=True)

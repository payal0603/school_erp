from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class TimetableReport(models.TransientModel):
	_name = "time.table.report"
	_description = "Generate Time Table Report"

	state = fields.Selection(
		[('teacher', 'Teacher'), ('student', 'Student')],
		string='Select', required=True, default='teacher')
	standard_id = fields.Many2one('student.class', string='Standard')
	division_id = fields.Many2one('student.division', string='Division')
	teacher_id = fields.Many2one('student.teacher', string='Teacher')
	start_date = fields.Date(
		string='Start Date', required=True,
		default=(datetime.today() - relativedelta(
			days=datetime.date(
				datetime.today()).weekday())).strftime('%Y-%m-%d'))
	end_date = fields.Date(
		string='End Date', required=True,
		default=(datetime.today() + relativedelta(days=6 - datetime.date(
			datetime.today()).weekday())).strftime('%Y-%m-%d'))

	@api.constrains('start_date', 'end_date')
	def _check_dates(self):
		for session in self:
			start_date = fields.Date.from_string(session.start_date)
			end_date = fields.Date.from_string(session.end_date)
			if end_date < start_date:
				raise ValidationError(_('End Date cannot be set before \
				Start Date.'))
			elif end_date > (start_date + timedelta(days=6)):
				raise ValidationError(_("Select date range for a week!"))

	# @api.onchange('standard_id')
	# def onchange_standard(self):
	# 	if self.division_id and self.standard_id:
	# 		if self.standard_id.division_id != self.standard_id:
	# 			self.standard_id = False

	def gen_time_table_report(self):
		template = self.env.ref(
			'school_management.report_teacher_timetable_generate')
		data = self.read(['start_date', 'end_date', 'standard_id', 'division_id', 'state','teacher_id'])[0]
		print("<<<<<<<<<<<<DATASSSSSSSSSS>>>>>>>>>>>>>>>>>>>",data)
		if data['state'] == 'student':
			print("<<<<<<<<<<<<DATASSSSSSSSSS1111>>>>>>>>>>>>>>>>>>>",data)
			time_table_ids = self.env['student.timetable'].search(
				[('standard_id', '=', data['standard_id'][0]),
				 ('division_id', '=', data['division_id'][0]),
				 ('start_time', '>=', data['start_date']),
				 ('end_time', '<=', data['end_date'])],
				order='start_time asc')
			data.update({'time_table_ids': time_table_ids.ids})
			print("<<<<<<<<<<<<DATASSSSSSSSSS22222222>>>>>>>>>>>>>>>>>>>",data)
			template = self.env.ref(
				'school_management.report_student_timetable_generate')
		else:
			teacher_time_table_ids = self.env['student.timetable'].search(
				[('start_time', '>=', data['start_date']),
				 ('end_time', '<=', data['end_date']),
				 ('teacher_id', '=', data['teacher_id'][0])],
				order='start_time asc')
			data.update({'teacher_time_table_ids': teacher_time_table_ids.ids})
		return template.report_action(self, data=data)
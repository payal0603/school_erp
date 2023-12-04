from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime


class StudentExamSession(models.Model):
	_name = "student.exam.session"
	_inherit = ["mail.thread"]
	_description = "Exam Session"

	name = fields.Char(string="Exam Session", required=True, tracking=True)
	standard_id = fields.Many2one('student.class', string="Standard", required=True, tracking=True)
	code = fields.Char(string="Exam Session Code", required=True, tracking=True)
	start_date = fields.Date(string="Start Date", required=True, tracking=True)
	end_date = fields.Date(string="End Date", required=True, tracking=True)
	exam_ids = fields.One2many('student.exam', 'session_id', string="Exam(s)")
	exam_type = fields.Selection([
		('annual', 'Annual'),
		('midterm', 'Midterm'),
		('quarterly', 'Quarterly')], string="Exam Type", tracking=True, default="annual")
	evaluation_type = fields.Selection([
		('normal', 'Normal'),
		('grade', 'Grade')], string="Evaluation Type", tracking=True, default='normal')
	state = fields.Selection([
		('draft', 'Draft'),
		('schedule', 'Schedule'),
		('held', 'Held'),
		('cancel', 'Cancel'),
		('done', 'Done')], string='Status', default="draft", tracking=True)
	active = fields.Boolean(string="Active", default=True)

	def _get_report_base_filename(self):
		return self.name 

	@api.constrains('start_date', 'end_date')
	def _check_date(self):
		if self.start_date > self.end_date:
			raise ValidationError(_("End Date can't Be Set Before Start Date"))

	def act_draft(self):
		self.state = 'draft'

	def act_schedule(self):
		self.state = 'schedule'

	def act_held(self):
		self.state = 'held'

	def act_done(self):
		self.state = 'done'

	def act_cancel(self):
		self.state = 'cancel'


class StudentExam(models.Model):
	_name = "student.exam"
	_inherit = ["mail.thread"]
	_description = "Exam Timing"

	name = fields.Char(string="Exam", required=True)
	session_id = fields.Many2one('student.exam.session', string="Exam Session", domain=[('state', 'not in', ['cancel', 'done'])])
	standard_id = fields.Many2one('student.class', string="Standard", related="session_id.standard_id", required=True)
	subject_id = fields.Many2one('student.subject', string="Subject", tracking=True)
	code = fields.Char(string="Exam Code", required=True)
	start_time = fields.Datetime(string="Start Time", required=True)
	end_time = fields.Datetime(string="End Time", required=True)
	state = fields.Selection([
		('draft', 'Draft'),
		('held', 'Held'),
		('result_updated', 'Result Updated'),
		('cancel', 'Cancel'),
		('done', 'Done')], string="Status", default='draft', readonly=True, tracking=True)
	responsible_id = fields.Many2one('student.teacher', string="Responsible")
	total_marks = fields.Integer(string='Total Marks', required=True)
	min_marks = fields.Integer(string='Passing Marks', required=True)
	attendees_line_ids = fields.One2many('student.exam.attendees', 'exam_id', string='Attendees', readonly=True)
	active = fields.Boolean(default=True)

	def name_get(self):
		result = []
		for rec in self:
			# name = "[" + rec.grno +"]" +" "+ rec.name
			name = rec.name +" [ "+ rec.code  +" ]"
			result.append((rec.id, name))
		return result

	@api.constrains('total_marks', 'min_marks')
	def _check_marks(self):
		if self.total_marks <= 0.0 or self.min_marks <=0.0:
			raise ValidationError(_("Enter Proper Marks"))
		if self.min_marks > self.total_marks:
			raise ValidationError(_("Passing Marks Can't Be Greater Than Total Marks"))

	@api.constrains('start_time', 'end_time')
	def _check_date_time(self):
		session_start = datetime.datetime.combine(fields.Date.from_string(self.session_id.start_date),datetime.time.min)
		session_end = datetime.datetime.combine(fields.Date.from_string(self.session_id.end_date),datetime.time.max)
		start_time = fields.Datetime.from_string(self.start_time)
		end_time = fields.Datetime.from_string(self.end_time)
		if start_time > end_time:
			raise ValidationError(_('End Time cannot be set before Start Time.'))
		elif start_time < session_start or start_time > session_end or \
				end_time < session_start or end_time > session_end:
			raise ValidationError(_('Exam Time should in between Exam Session Dates.'))

	def act_result_updated(self):
		self.state = 'result_updated'

	def act_done(self):
		self.state = 'done'

	def act_draft(self):
		self.state = 'draft'

	def act_cancel(self):
		self.state = 'cancel'
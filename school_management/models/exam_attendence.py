from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StudentExamAttendence(models.Model):
	_name = 'student.exam.attendees'
	_inherit = ["mail.thread"]
	_description = "Exam Timing"

	name = fields.Char(string="name")
	student_id = fields.Many2one('student.student', string="Student Name", required=True)
	status = fields.Selection([
		('present', 'Present'),
		('absent', 'Absent')], string="Status", default='present', required=True)
	marks = fields.Integer(string="Marks")
	exam_id = fields.Many2one('student.exam', string="Exam", required=True, ondelete="cascade", domain=[('state', '!=', 'done')])
	standard_id = fields.Many2one('student.class', string="Standard")
	division_id = fields.Many2one('student.division', string="Division")
	active = fields.Boolean(default=True)

	@api.constrains('marks')
	def _check_marks(self):
		if self.marks < 0.0:
			raise ValidationError(_("Enter Valid Marks"))

	@api.onchange('exam_id')
	def onchange_exam(self):
		self.standard_id = self.exam_id.session_id.standard_id
		self.student_id = False

	@api.onchange('status')
	def onchange_marks(self):
		if self.status == 'absent':
			self.marks = 0
			return {'attrs': {'readonly': True}}
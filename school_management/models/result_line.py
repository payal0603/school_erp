from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StudentResultLine(models.Model):
	_name = 'student.result.line'
	_inherit = ["mail.thread"]
	_rec_name = 'marks'
	_description = "Result Line"

	marksheet_line_id = fields.Many2one('student.marksheet.line', string="Marksheet Line", ondelete="cascade")
	exam_id = fields.Many2one('student.exam', string="Exam ID", required=True)
	evaluation_type = fields.Selection(related="exam_id.session_id.evaluation_type", store=True)
	marks = fields.Integer(string="Marks", required=True)
	grade = fields.Char(string="Grade", readonly=True, compute='_compute_grade')      # 
	student_id = fields.Many2one('student.student', string="Student", required=True)
	status = fields.Selection([
		('pass', 'Pass'),
		('fail', 'Fail')], string="Status", store=True, default="pass", compute='_compute_status')      # 
	active = fields.Boolean(default=True)

	@api.constrains('marks')
	def _check_marks(self):
		if (self.marks < 0.0):
			raise ValidationError(_("Enter Proper Marks "))

	@api.depends('marks')
	def _compute_grade(self):
		for rec in self:
			if rec.evaluation_type == 'grade':
				grades = rec.marksheet_line_id.marksheet_reg_id.result_template_id.grade_ids
				if grades:
					for grade in grades:
						if grade.min_per <= rec.marks and grade.max_per >= rec.marks:
							rec.grade = grade.result
				else:
					rec.grade = None
			else:
				rec.grade = None

	@api.depends('marks')
	def _compute_status(self):
		for rec in self:
			rec.status = 'pass'
			if rec.marks < rec.exam_id.min_marks :
				rec.status = 'fail'
			else:
				rec.status = 'pass'

	def unlink(self):
		for rec in self:
			super(StudentResultLine, rec).unlink()
		return self
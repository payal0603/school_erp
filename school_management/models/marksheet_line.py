from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StudentMarksheetLine(models.Model):
	_name = 'student.marksheet.line'
	_inherit = ["mail.thread"]
	_description = "Marksheet Line"
	_rec_name = 'marksheet_reg_id'

	marksheet_reg_id = fields.Many2one('student.marksheet.register', string="Marksheet Register")
	evaluation_type = fields.Selection(related="marksheet_reg_id.exam_session_id.evaluation_type",string="Evaluation Type",  store=True)
	student_id = fields.Many2one('student.student', string='Student Name', required=True)
	result_line_ids = fields.One2many('student.result.line', 'marksheet_line_id', string="Results")
	total_marks = fields.Integer(string="Total Marks", store=True, compute="_compute_total_marks")# compute=""
	percentage = fields.Float(string="Percentage", store=True, compute="_compute_percentage")# compute=""
	generated_date = fields.Date(string="Generated Date", required="True", default=fields.Date.today())
	grade = fields.Char(string="Grade", readonly=True, compute="_compute_grade1")# compute
	status = fields.Selection([
		('pass', 'Pass'),
		('fail', 'Fail')], string="Status", store=True, default='fail', compute="_compute_status")# compute
	active = fields.Boolean(default=True)

	
	def get_rounded_value(self, value):
		return round(value, 2)

	@api.constrains('total_marks', 'percentage')
	def _check_marks(self):
		for rec in self:
			if (rec.total_marks < 0.0) or (rec.percentage < 0.0):
				raise ValidationError(_("Enter proper marks or percentage!"))

	@api.depends('result_line_ids.marks')
	def _compute_total_marks(self):
		for rec in self:
			rec.total_marks = sum([
				int(x.marks) for x in rec.result_line_ids])

	@api.depends('total_marks')
	def _compute_percentage(self):
		for rec in self:
			total_exam_marks = sum([int(x.exam_id.total_marks) for x in rec.result_line_ids])
			rec.percentage = rec.total_marks and (100 * rec.total_marks) / total_exam_marks or 0.0

	@api.depends('percentage')
	def _compute_grade1(self):
		for rec in self:
			grade1 = ''
			if rec.evaluation_type == 'grade':
				grades = rec.marksheet_reg_id.result_template_id.grade_ids
				for grade in grades:
					if grade.min_per <= rec.percentage <= grade.max_per:
						grade1 = grade.result
			rec.grade = grade1

	@api.depends('result_line_ids.status')
	def _compute_status(self):
		for rec in self:
			rec.status = 'pass'
			for result in rec.result_line_ids:
				if result.status == 'fail':
					rec.status = 'fail'


	def _get_report_base_filename(self):
		return self.student_id.name + "Marksheet"
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StudentGradeConfiguration(models.Model):
	_name = 'student.grade.configuration'
	_description = 'Grade Configuration'

	min_per = fields.Integer(string="Minimum Percentage", required=True)
	max_per = fields.Integer(string="Maximum Percentage", required=True)
	result = fields.Char(string="Result(Grade)", required=True)

class StudentResultTemplate(models.Model):
	_name = 'student.result.template'
	_inherit = ["mail.thread"]
	_description = "Result Template"

	name = fields.Char(string="Name", required=True)
	exam_session_id = fields.Many2one('student.exam.session', string="Exam Session", required=True, tracking=True)
	evaluation_type = fields.Selection(related="exam_session_id.evaluation_type", string="Evaluation Type", store=True, tracking=True)
	result_date = fields.Date(string="Result Date", required=True, default=fields.Date.today(), tracking=True)
	grade_ids = fields.Many2many('student.grade.configuration', string="Grades")
	state = fields.Selection([
		('draft', 'Draft'),
		('result_genrated', 'Result Generated')], string="Status", default='draft')
	active = fields.Boolean(default=True)

	@api.constrains('exam_session_id')
	def _check_exam_session(self):
		for rec in self:
			for exam in rec.exam_session_id.exam_ids:
				if exam.state != 'done':
					raise ValidationError(_('All Subject Exam Should Be Done'))

	@api.constrains('grade_ids')
	def _check_min_max_percentage(self):
		for rec in self:
			cnt = 0
			for grade in rec.grade_ids:
				for sub_grade in rec.grade_ids:
					if grade != sub_grade:
						if (sub_grade.min_per <= grade.min_per) and (sub_grade.max_per >= grade.min_per) \
							or (sub_grade.min_per <= grade.max_per) and (sub_grade.max_per >= grade.max_per):
							cnt += 1

			if cnt > 0:
				raise ValidationError('Percentage Range Is Conflict With Other Record')


	def generate_result(self):
		for rec in self:
			marksheet_reg_id = self.env['student.marksheet.register'].create(
			{
				'name': 'Mark Sheet for %s' % rec.exam_session_id.name,
				'exam_session_id': rec.exam_session_id.id,
				'generated_date': fields.Date.today(),
				'state': 'draft',
				'result_template_id': rec.id
			})
			student_dict = {}
			for exam in rec.exam_session_id.exam_ids:
				for attendee in exam.attendees_line_ids:
					result_line_id = self.env['student.result.line'].create({
						'student_id': attendee.student_id.id,
						'exam_id': exam.id,
						'marks': str(attendee.marks and attendee.marks or 0),
					})
					if attendee.student_id.id not in student_dict:
						student_dict[attendee.student_id.id] = []
					student_dict[attendee.student_id.id].append(result_line_id)

			for student in student_dict:
				marksheet_line_id = self.env['student.marksheet.line'].create({
					'student_id': student,
					'marksheet_reg_id': marksheet_reg_id.id,
				})
				for result_line in student_dict[student]:
					result_line.marksheet_line_id = marksheet_line_id
			rec.state = 'result_genrated'
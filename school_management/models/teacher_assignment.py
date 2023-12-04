from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolTeacherAssignment(models.Model):

	_name = "school.teacher.assignment"
	_inherit = ["mail.thread"]
	_description = "Teacher Assignment Information"

	name = fields.Char(string="Assignment Name", required=True)
	subject_id = fields.Many2one('student.subject', string="Subject", required=True)
	standard_id = fields.Many2one('student.class', string="Standard", required=True, store=True)
	division_id = fields.Many2many('student.division', string="Division", required=True)
	teacher_id = fields.Many2one('student.teacher', string="Teacher Name", required=True)
	assign_date = fields.Date(string="Assign Date", default=fields.Date.today(), required=True)
	due_date = fields.Date(string="Due Date", required=True)
	description = fields.Text(string="Description", required=True, help="Description Or Question For Homework")
	attached_homework = fields.Binary(string="Attach Assignment")
	state = fields.Selection([
		('draft', 'Draft'),
		('active', 'Active'),
		('done', 'Done')], string="Status", default='draft')
	student_assignment_ids = fields.One2many('school.student.assignment', 'teacher_assignment_id', string="Student Assignment")
	submission_type = fields.Selection([
		('hardcopy', 'Hardcopy(Paperwork)'),
		('softcopy', 'Softcopy')], string="Submission Type", default='hardcopy')
	active = fields.Boolean(default=True)

	@api.constrains("assign_date", "due_date")
	def check_date(self):
		if self.due_date < self.assign_date:
			raise ValidationError(_("Due date of homework should be greater than Assign date!"))

	def done_assignments(self):
		self.state = 'done'

	def active_assignment(self):
		student_obj = self.env['student.student']
		search_domain = [('standard_id', '=', self.standard_id.id),('division_id', 'in', self.division_id.ids)]
		student_ids = student_obj.search(search_domain)
		student_list = []
		for std in student_ids:
			data = {
				'teacher_assignment_id': self.id,
				'subject_id': self.subject_id.id,
				'standard_id': self.standard_id.id,
				'teacher_id': self.teacher_id.id,
				'assign_date': self.assign_date,
				'due_date': self.due_date,
				'state': 'draft',
				'submission_type': self.submission_type,
				'student_id': std.id,
				'division_id': std.division_id.id


			}
			student_list.append((0,0,data))
		self.student_assignment_ids = student_list

		self.write({'state': 'active'})
		# vals = {

		# }
		# print("VALSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",vals)
		# stud = self.env['school.student.assignment'].create(vals)
		# 
	def unlink(self):
		for rec in self:
			if self.state != 'draft':
				raise ValidationError(_('Confirmed Assignment Can Not Be Delete'))
		return super(SchoolTeacherAssignment, self).unlink()
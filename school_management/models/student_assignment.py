from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class SchoolStudentAssignment(models.Model):

	_name = "school.student.assignment"
	_inherit = ["mail.thread"]
	_description = "student Assignment Information"

	name = fields.Char(string="Assignment Name")
	teacher_assignment_id = fields.Many2one('school.teacher.assignment', string="Teacher Assignments", required=True,  domain=[('state', '!=', 'done')])  
	subject_id = fields.Many2one('student.subject', string="Subject", related="teacher_assignment_id.subject_id", required=True)
	standard_id = fields.Many2one('student.class', string="Standard", related="teacher_assignment_id.standard_id", required=True)
	division_id = fields.Many2one('student.division', string="Division", required=True)
	rejection_reason = fields.Char(string="Reason To reject")
	teacher_id = fields.Many2one("student.teacher", string="Teacher",related="teacher_assignment_id.teacher_id", required=True)
	assign_date = fields.Date(string="Assign Date", required=True, related="teacher_assignment_id.assign_date")
	due_date = fields.Date(string="Due Date", required=True, related="teacher_assignment_id.due_date")
	state = fields.Selection([
		("draft", "Draft"),
		("active", "Active"),
		("reject", "Reject"),
		("done", "Done")], string="Status", default="draft",
		help="States of assignment")
	student_id = fields.Many2one("student.student", string="Student", required=True)
	# stud_roll_no = fields.Integer(string="Roll no")
	submission_type = fields.Selection([
		("hardcopy", "Hardcopy(Paperwork)"),
		("softcopy", "Softcopy")], string="Submission Type", related="teacher_assignment_id.submission_type")
	attachfile_format = fields.Char(string="Submission File Format")
	submit_assign = fields.Binary(string="Submit Assignment")
	file_name = fields.Char(string="File Name")
	active = fields.Boolean(default=True)


	@api.constrains("assign_date", "due_date")
	def check_date(self):
		if self.due_date < self.assign_date:
			raise ValidationError(_("Due date of homework should be greater than Assign date!"))

	def _get_student_domain(self):
		return [('student_id', '=', self.env.user.id)]


	@api.constrains("submit_assign", "file_name")
	def check_file_format(self):
		if self.submission_type == 'softcopy':
			if self.file_name:
				file_format = self.file_name.split(".")
				if len(file_format) == 2:
					file_format = file_format[1]
				else:
					raise ValidationError(_("Kindly attach file with format: %s!")% self.attachfile_format)
				if (file_format in self.attachfile_format or
						self.attachfile_format in file_format):
					return True
				raise ValidationError(_("Kindly attach file with format: %s!")% self.attachfile_format)

	def write(self, vals):
		if self.env.user.has_group('school_management.group_school_student') and self.state == 'done':
			raise UserError("Cannot update a record in 'done' state.")
		return super(SchoolStudentAssignment, self).write(vals)

	@api.onchange("student_id")
	def onchange_student_standard(self):
		self.standard_id = self.student_id.standard_id.id

	def active_assignment(self):
		if self.submission_type == "softcopy" and not self.submit_assign:
			raise ValidationError(_("Kindly Attach Homework!"))
		self.state = "active"

	def done_assignment(self):
		if self.submission_type == "softcopy" and not self.submit_assign:
			raise ValidationError(_("You Have Not Attached The Homework! Please Attach The Homework!"))
		self.state = "done"

	def reassign_assignment(self):
		self.ensure_one()
		self.state = "active"

	def unlink(self):
		for rec in self:
			if rec.state == "done":
				raise ValidationError(_("Confirmed Assignment Can Not Be Deleted!"))
		return super(SchoolStudentAssignment, self).unlink()
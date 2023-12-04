from odoo import models, fields


class ResCompany(models.Model):
	_inherit = "res.company"

	signature = fields.Binary('Signature')
	accreditation = fields.Text('Accreditation')
	approval_authority = fields.Text('Approval Authority')


class ResUsers(models.Model):
	_inherit = "res.users"

	def _department_count(self):
		return self.env['student.department'].sudo().search_count([])

	student_id = fields.Many2one('student.student', string='Student ID')
	teacher_id = fields.Many2one('student.teacher', string="Teacher ID")
	user_line = fields.One2many('student.student', 'user_id', string='User Line')
	child_ids = fields.Many2many(
		'res.users', 'res_user_first_rel1',
		'user_id', 'res_user_second_rel1', string='Childs')
	dept_id = fields.Many2one('student.department', string='Department Name')
	department_count = fields.Integer(compute='_compute_department_count',
									  string="Number of Departments",
									  default=_department_count)

	def create_user(self, records, user_group=None):
		for rec in records:
			if not rec.user_id:
				user_vals = {
					'name': rec.name,
					'login': rec.email or (rec.name + rec.last_name),
					'partner_id': rec.partner_id.id,
					'dept_id': rec.main_department_id.id,
				}
				user_id = self.create(user_vals)
				rec.user_id = user_id
				if user_group:
					user_group.users = user_group.users + user_id

	def _compute_department_count(self):
		department_count = self._department_count()
		for user in self:
			user.department_count = department_count

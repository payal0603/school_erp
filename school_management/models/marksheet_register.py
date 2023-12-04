from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class studentMarksheetRegister(models.Model):
	_name = "student.marksheet.register"
	_inherit = ["mail.thread"]
	_description = "Marksheet Register"

	exam_session_id = fields.Many2one('student.exam.session', string="Exam Session", required=True,)
	marksheet_line_ids = fields.One2many('student.marksheet.line', 'marksheet_reg_id', string="Marksheets", required=True, tracking=True)
	generated_date = fields.Date(string="Generated Date", required=True, tracking=True, default=fields.Date.today())
	state = fields.Selection([
		('draft', 'Draft'),
		('validate', 'Validate'),
		('cancel', 'Cancel')], string="Status", default='draft', required=True, tracking=True)
	total_pass = fields.Integer(string="Total Pass", tracking=True, store=True, compute="_compute_total_pass")
	total_fail = fields.Integer(string="Total Fail", tracking=True, store=True, compute="_compute_total_fail")
	name = fields.Char(string="Marksheet Register", required=True, tracking=True)
	result_template_id = fields.Many2one('student.result.template', string="Result Template", required=True, tracking=True)
	active = fields.Boolean(default=True)


	@api.constrains('total_pass', 'total_fail')
	def _check_pass_fail(self):
		for rec in self:
			if (rec.total_pass < 0.0) or (rec.total_fail < 0.0):
				raise ValidationError(_("Enter Proper Number Of Pass And Fail "))

	@api.depends('marksheet_line_ids.status')
	def _compute_total_pass(self):
		for rec in self:
			cnt = 0
			for marksheet in rec.marksheet_line_ids:
				if marksheet.status == 'pass':
					cnt += 1
			rec.total_pass = cnt

	@api.depends('marksheet_line_ids.status')
	def _compute_total_fail(self):
		for rec in self:
			cnt = 0
			for marksheet in rec.marksheet_line_ids:
				if marksheet.status == 'fail':
					cnt += 1
			rec.total_fail = cnt

	def act_draft(self):
		self.state = 'draft'

	def act_cancel(self):
		self.state = 'cancel'

	def act_validate(self):
		self.state = 'validate'
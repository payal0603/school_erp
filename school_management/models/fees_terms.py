from odoo import models, api, fields, exceptions, _


class StudentFeesTermsLine(models.Model):
	_name = "student.fees.terms.line"
	_rec_name = "due_days"
	_description = "Fees Details Line"

	due_days = fields.Integer(string='Due Days')
	due_date = fields.Date(string='Due Date')
	value = fields.Float(string='Value (%)')
	fees_element_line = fields.One2many("student.fees.element",
										"fees_terms_line_id", string="Fees Elements")
	fees_id = fields.Many2one('student.fees.terms', string='Fees')


class StudentFeesTerms(models.Model):
	_name = "student.fees.terms"
	_inherit = "mail.thread"
	_description = "Fees Terms For Standard"

	name = fields.Char(string='Fees Terms', required=True)
	active = fields.Boolean(string='Active', default=True)
	fees_terms = fields.Selection([
		('fixed_days', 'Fixed Fees of Days'),
		('fixed_date', 'Fixed Fees of Dates')], string='Term Type', default='fixed_days')
	note = fields.Text(string='Description')
	no_days = fields.Integer(string='No of Days')
	day_type = fields.Selection([
		('before', 'Before'), 
		('after', 'After')],string='Type')
	company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda s: s.env.user.company_id)
	line_ids = fields.One2many('student.fees.terms.line', 'fees_id', 'Terms')
	discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)

	@api.model
	def create(self, vals):
		res = super(StudentFeesTerms, self).create(vals)
		if not res.line_ids:
			raise exceptions.AccessError(_("Fees Terms must be Required!"))
		total = 0.0
		for line in res.line_ids:
			if line.value:
				total += line.value
		if total != 100.0:
			raise exceptions.AccessError(
				_("Fees terms must be divided as such sum up in 100%"))
		return res


class StudentStandardInherit(models.Model):
	_inherit = "student.class"

	fees_term_id = fields.Many2one('student.fees.terms', string='Fees Term')
	fees_start_date = fields.Date(string='Fees Start Date')

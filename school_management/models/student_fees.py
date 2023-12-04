from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StudentFeesDetails(models.Model):
	_name = "student.fees.details"
	_description = "Student Fees Details"
	_rec_name = 'student_id'

	fees_line_id = fields.Many2one('student.fees.terms.line', string='Fees Term Line')
	fees_term_id = fields.Many2one('student.fees.terms', string='Fees Terms')
	invoice_id = fields.Many2one('account.move', string='Invoice ID')
	amount = fields.Monetary(string='Fees Amount', currency_field='currency_id', required=True)
	date = fields.Date(string='Submit Date', required=True)
	product_id = fields.Many2one('product.product', string='Product')
	student_id = fields.Many2one('student.student', string='Student')
	fees_factor = fields.Float(string="Fees Factor")
	state = fields.Selection([
		('draft', 'Draft'),
		('invoice', 'Invoice Created'),
		('cancel', 'Cancel')], string='Status', copy=False)
	invoice_state = fields.Selection(related="invoice_id.state", string='Invoice Status', readonly=True)
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
	after_discount_amount = fields.Monetary(compute="_compute_discount_amount", currency_field='currency_id', string='After Discount Amount')
	discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
	course_id = fields.Many2one('student.class', string='Standard', required=False) 
	
	@api.depends('discount')
	def _compute_discount_amount(self):
		for discount in self:
			discount_amount = discount.amount * discount.discount / 100.0
			discount.after_discount_amount = discount.amount - discount_amount

	@api.depends('company_id')
	def _compute_currency_id(self):
		main_company = self.env['res.company']._get_main_company()
		for template in self:
			template.currency_id = \
				template.company_id.sudo().currency_id.id or main_company.currency_id.id

	currency_id = fields.Many2one(
		'res.currency', string='Currency', compute='_compute_currency_id',
		default=lambda self: self.env.user.company_id.currency_id.id)

	def get_invoice(self):
		inv_obj = self.env['account.move']
		partner_id = self.student_id.partner_id
		account_id = False
		product = self.product_id
		if product.property_account_income_id:
			account_id = product.property_account_income_id.id
		if not account_id:
			account_id = product.categ_id.property_account_income_categ_id.id
		if not account_id:
			raise UserError(
				_('There is no income account defined for this product: "%s".'
				  'You may have to install a chart of account from Accounting'
				  ' app, settings menu.') % product.name)
		if self.amount <= 0.00:
			raise UserError(
				_('The value of the deposit amount must be positive.'))
		else:
			amount = self.amount
			name = product.name
		invoice = inv_obj.create({
			# 'partner_id': student.name,
			'move_type': 'out_invoice',
			'partner_id': partner_id.id,

		})
		element_id = self.env['student.fees.element'].search([
			('fees_terms_line_id', '=', self.fees_line_id.id)])
		for records in element_id:
			if records:
				line_values = {'name': records.product_id.name,
							   'account_id': account_id,
							   'price_unit': records.value * self.amount / 100,
							   'quantity': 1.0,
							   'discount': self.discount or False,
							   'product_uom_id': records.product_id.uom_id.id,
							   'product_id': records.product_id.id, }
				invoice.write({'invoice_line_ids': [(0, 0, line_values)]})

		if not element_id:
			line_values = {'name': name,
						   # 'origin': student.gr_no,
						   'account_id': account_id,
						   'price_unit': amount,
						   'quantity': 1.0,
						   'discount': self.discount or False,
						   'product_uom_id': product.uom_id.id,
						   'product_id': product.id}
			invoice.write({'invoice_line_ids': [(0, 0, line_values)]})

		invoice._compute_tax_totals_json()
		self.state = 'invoice'
		self.invoice_id = invoice.id
		return True

	def action_get_invoice(self):
		value = True
		if self.invoice_id:
			form_view = self.env.ref('account.view_move_form')
			tree_view = self.env.ref('account.view_invoice_tree')
			value = {
				'domain': str([('id', '=', self.invoice_id.id)]),
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'account.move',
				'view_id': False,
				'views': [(form_view and form_view.id or False, 'form'),
						  (tree_view and tree_view.id or False, 'tree')],
				'type': 'ir.actions.act_window',
				'res_id': self.invoice_id.id,
				'target': 'current',
				'nodestroy': True
			}
		return value


class StudentStudent(models.Model):
	_inherit = "student.student"

	fees_detail_ids = fields.One2many('student.fees.details', 'student_id', tracking=True, string='Fees Collection Details')
	fees_details_count = fields.Integer(compute='_compute_fees_details')
	# total_invoiced = fields.Integer(string="Total invoiced")
	# invoice_ids = fields.Many2many('account.move', string='Invoice ID')

	@api.depends('fees_detail_ids')
	def _compute_fees_details(self):
		for fees in self:
			fees.fees_details_count = self.env['student.fees.details'].search_count(
				[('student_id', '=', self.id)])

	def count_fees_details(self):
		return {
			'type': 'ir.actions.act_window',
			'name': 'Fees Details',
			'view_mode': 'tree',
			'res_model': 'student.fees.details',
			'context': {'create': False},
			'domain': [('student_id', '=', self.id)],
			'target': 'current',
		}

	def action_view_invoice(self):
		result = self.env.ref('account.action_move_out_invoice_type')
		fees = result and result.id or False
		result = self.env['ir.actions.act_window'].browse(fees).read()[0]
		inv_ids = []
		for student in self:
			inv_ids += [invoice.id for invoice in student.invoice_ids]
			result['context'] = {'default_partner_id': student.partner_id.id}
		if len(inv_ids) > 1:
			result['domain'] = \
				"[('id','in',[" + ','.join(map(str, inv_ids)) + "])]"
		else:
			res = self.env.ref('account.view_move_form')
			result['views'] = [(res and res.id or False, 'form')]
			result['res_id'] = inv_ids and inv_ids[0] or False
		return result

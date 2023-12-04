from odoo import models, fields


class StudentFeesElementLine(models.Model):
    _name = "student.fees.element"
    _description = "Fees Element for Standard"

    sequence = fields.Integer(string='Sequence')
    product_id = fields.Many2one('product.product', string='Product(s)', required=True)
    value = fields.Float(string='Amount')
    department_id = fields.Many2one('student.department', string="Educational Medium")
    fees_terms_line_id = fields.Many2one('student.fees.terms.line', string='Fees Terms')


class StudentStandard(models.Model):
    _inherit = "student.class"

    fees_term_id = fields.Many2one('student.fees.terms', string='Fees Term')

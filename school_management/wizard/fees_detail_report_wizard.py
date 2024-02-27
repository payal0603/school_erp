from odoo import models, fields


class FeesDetailReportWizard(models.TransientModel):
	_name = "fees.detail.report.wizard"
	_description = "Wizard For Fees Details Report"

	fees_filter = fields.Selection(
		[('student', 'Student'), ('standard', 'Standard')],
		'Fees Filter', required=True)
	student_id = fields.Many2one('student.student', string='Student')
	standard_id = fields.Many2one('student.class', string='Standard')

	def print_report(self):
		data = {}
		if self.fees_filter == 'student':
			data['fees_filter'] = self.fees_filter
			data['student'] = self.student_id.id
		else:
			data['fees_filter'] = self.fees_filter
			data['standard'] = self.standard_id.id

		report = self.env.ref(
			'school_management.action_report_fees_detail_analysis')
		return report.report_action(self, data=data)

import time
from odoo import models, api, fields


class ReportMarksheetReport(models.AbstractModel):
	_name = "report.school_management.report_marksheet_report"
	_description = "Exam Marksheet Report"

	def get_objects(self, objects):
		obj = []
		for data in objects:
			obj.extend(data)
		return obj

	def get_lines(self, obj):
		lines = []
		for line in obj.result_line_ids:
			lines.extend(line)
		return lines

	def get_date(self, date):
		date1 = fields.Date.to_date(date)
		return str(date1.month) + ' / ' + str(date1.year)

	def get_total(self, result_line_ids):
		total = [x.exam_id.total_marks for x in result_line_ids]
		return sum(total)

	def get_rounded_value(self, value):
		return round(value, 2)

	@api.model
	def _get_report_values(self, docids, data):
		docs = self.env['student.marksheet.line'].browse(docids)
		docargs = {
			'doc_model': 'student.marksheet.line',
			'docs': docs,
			'time': time,
			'get_objects': self.get_objects,
			'get_lines': self.get_lines,
			'get_date': self.get_date,
			'get_total': self.get_total,
		}
		return docargs

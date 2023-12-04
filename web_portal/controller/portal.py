from odoo.addons.portal.controllers.portal import CustomerPortal, pager
from odoo.http import request
from odoo import http, fields, _
import datetime
import base64


class StudentPortal(CustomerPortal):

	@http.route()
	def web_login(self, redirect=None, *args, **kw):
		response = super(OpeneducatHome, self).web_login(
			redirect=redirect, *args, **kw)
		if not redirect and request.params['login_success']:
			if request.env['res.users'].browse(request.uid).has_group(
					'base.group_user'):
				redirect = b'/web?' + request.httprequest.query_string
			else:
				if request.env.user.is_parent:
					redirect = '/my/child'
				else:
					redirect = '/my/home'
			return werkzeug.utils.redirect(redirect)
		return response

	def _login_redirect(self, uid, redirect=None):
		if redirect:
			return super(OpeneducatHome, self)._login_redirect(uid, redirect)
		if request.env.user.is_parent:
			return '/my/child'
		return '/my/home'

	def _prepare_home_portal_values(self, counters):

		res = super(StudentPortal, self)._prepare_home_portal_values(counters)
		print("_prepare_home_portal_values is Called .......... ", res)
		res['student_counts'] = request.env['student.student'].search_count([])
		return res

	def _get_sale_searchbar_sortings(self):
		return {
			'attendence_date': {'label': _('Order Date'), 'order': 'attendence_date desc'},
			'present': {'label': _('Present'), 'order': 'present'},
			'absent': {'label': _('Absent'), 'order': 'absent'},
		}

	@http.route(['/my/students'], type='http', auth='user', website=True)
	def StudentMenuListView(self, **kw):
		print("def student list view has been Called ......... ")
		student_obj = request.env['student.student']
		students = student_obj.search([])
		vals = {'students' : students, 'page_name' : 'student_profile_list_view', 'user': request.env.user}
		return request.render("web_portal.students_profile_list_view_portal", vals)

	# @http.route(['/my/students/<model("student.student"):student_id>'], type='http', auth='user', website=True)
	# def StudentListView(self, **kw):
	# 	# print("def student list view has been Called ......... ")
	# 	student_obj = request.env['student.student']
	# 	students = student_obj.search([])
	# 	vals = {'students' : students, 'page_name' : 'student_list_view', 'user': request.env.user}
	# 	return request.render("web_portal.students_list_view_portal", vals)


	@http.route([
		'/my/students/<model("student.student"):student_id>'], type="http", auth='user', website=True)
	def StudentFormView(self, student_id, **kw):
		print("Form View Controller has been called .........")
		vals = {'student' : student_id, 'page_name' : 'student_form_view', 'user': request.env.user}
		return request.render("web_portal.students_form_view_portal", vals)

	@http.route([
		'/my/students/print/<model("student.student"):student_id>'], type="http", auth='user', website=True)
	def StudentIdPrint(self, student_id, **kw):
		print("Student Print Report Function is Called")
		return self._show_report(model=student_id, report_type='pdf',
								 report_ref="school_management.report_student_idcard",
								 download=True)

	@http.route([
		'/my/education_info/<model("student.student"):student_id>'], type="http", auth='user', website=True)
	def EducationFormView(self, student_id, **kw):
		print("Education Form View Controller has been called .........")
		print("<<<<<<<<<<Student", student_id)
		vals = {'student' : student_id, 'page_name' : 'education_form_view', 'user': request.env.user}
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", vals)
		return request.render("web_portal.education_form_view_portal", vals)

	@http.route([
		'/my/parents/<model("student.student"):student_id>'], type="http", auth='user', website=True)
	def ParentsFormView(self, student_id, **kw):
		print("Education Form View Controller has been called .........")
		print("<<<<<<<<<<Student", student_id)
		parent_obj = request.env['student.parent']
		parents = parent_obj.search([('student_ids.id', '=', student_id.id)])
		vals = {'parent' : parents, 'page_name' : 'parent_form_view', 'user': request.env.user}
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", vals)
		return request.render("web_portal.parents_form_view_portal", vals)

		# attendance_sheet

	@http.route([
		'/my/attendance_sheet/<model("student.student"):student_id>'], type="http", auth='user', website=True) # , '/my/attendance_sheet/<model("student.student"):student_id>/page/<int:page>'
	def AttendenceSheetListView(self, student_id, sortby="attendence_date", search="", search_in="All", **kw):                           #page=1, 
		print("Attendence sheet Form View Controller has been called .........")
		print("<<<<<<<<<<Student", student_id)

		# sorted_list = {

		# 	'attendence_date': {'label': 'Date Asc', 'order': 'attendence_date desc'},
		# 	# 'present': {'label': '', 'order': 'date desc'},
		# 	# 'absent': {'label': '', 'order': 'date desc'}

		# }

		searchbar_sortings = self._get_sale_searchbar_sortings()

		search_list = {

			'All': {'label': 'Date Asc', 'input': 'All', 'domain': []},
			'Present': {'label': 'Present', 'input': 'Present', 'domain': [('present', '=', True)]},
			'Absent': {'label': 'Absent', 'input': 'Absent', 'domain': [('absent', '=', True)]},

		}

		search_domain = search_list[search_in]['domain']

		sort_order = searchbar_sortings[sortby]['order']
		student_obj = request.env['student.attendence.line']
		total_attendance = student_obj.search_count(search_domain)
		page_detail = pager(url = '/my/attendance_sheet/<model("student.student"):student_id>',
							total = total_attendance,
							url_args = {'sortby': sortby, 'search_in': search_in, 'search': search}
							)

		students = student_obj.search([('student_id.id', '=', student_id.id)] + search_domain, order=sort_order, offset=page_detail['offset'])			#, limit=5, offset=page_detail['offset']
		vals = {'students' : students, 'page_name' : 'attendence_list_view', 'user': request.env.user, 
				'sortby': sortby, 
				'searchbar_sortings': searchbar_sortings,
				'search_in': search_in,
				'searchbar_inputs': search_list,
				'search': search} 		# , 'pager': page_detail
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", vals)
		return request.render("web_portal.attendence_list_view_portal", vals)

	@http.route([
		'/my/marksheet/<model("student.student"):student_id>'], type="http", auth='user', website=True)
	def marksheetFormView(self, student_id, **kw):
		print("Marksheet Form View Controller has been called .........")
		print("<<<<<<<<<<Student", student_id)
		student_obj = request.env['student.marksheet.line']
		students = student_obj.search([('student_id.id', '=', student_id.id)])
		vals = {'students' : students, 'page_name' : 'marksheet_form_view', 'user': request.env.user}
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", vals)
		return request.render("web_portal.marksheet_form_view_portal", vals)

	@http.route([
		'/my/marksheet/print/<model("student.marksheet.line"):student_id>'], type="http", auth='user', website=True)
	def StudentIdPrint(self, student_id, **kw):
		print("Student Print Report Function is Called")
		return self._show_report(model=student_id, report_type='pdf',
								 report_ref="school_management.report_marksheet_report",
								 download=True)

	@http.route([
		'/my/exam_session/<model("student.student"):student_id>'], type="http", auth='user', website=True)
	def ExamSessionFormView(self, student_id, **kw):
		print("exam Form View Controller has been called .........")
		print("<<<<<<<<<<Student", student_id)
		student = request.env['student.student'].sudo().search([('user_id', '=', request.uid)], limit=1)
		student_obj = request.env['student.exam.session']
		students = student_obj.search([('standard_id.id', '=', student.standard_id.id)])
		vals = {'students' : students, 'page_name' : 'exam_session_form_view', 'user': request.env.user}
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", vals)
		return request.render("web_portal.exam_session_form_view_portal", vals)


	# @http.route([
	# 	'/my/exam_session/print/<model("student.exam.session"):student_id>'], type="http", auth='user', website=True)
	# def StudentIdPrint(self, student_id, **kw):
	# 	print("Student Print Report Function is Called")
	# 	return self._show_report(model=student_id, report_type='pdf',
	# 							 report_ref="school_management.student_hall_ticket_report",
	# 							 download=True)

	@http.route([
		'/my/exam/<model("student.exam.session"):student_id>'], type="http", auth='user', website=True)
	def ExamFormView(self, student_id, **kw):
		print("exam Form View Controller has been called .........")
		print("<<<<<<<<<<Student", student_id)
		student = request.env['student.student'].sudo().search([('user_id', '=', request.uid)], limit=1)
		student_obj = request.env['student.exam']
		exams = student_obj.search([('standard_id.id', '=', student.standard_id.id),
									('session_id', '=', student_id.id)])
		vals = {'students' : exams, 'page_name' : 'exam_form_view', 'user': request.env.user}
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", vals)
		return request.render("web_portal.exam_form_view_portal", vals)

		# student.fees.details

	@http.route([
		'/my/fees/<model("student.student"):student_id>'], type="http", auth='user', website=True)
	def FeesDetailsFormView(self, student_id, **kw):
		print("fees Form View Controller has been called .........")
		print("<<<<<<<<<<Student", student_id)
		student_obj = request.env['student.fees.details']
		students = student_obj.search([('student_id.id', '=', student_id.id)])
		vals = {'students' : students, 'page_name' : 'fees_form_view', 'user': request.env.user}
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", vals)
		return request.render("web_portal.fees_form_view_portal", vals)

	@http.route([
		'/my/admissions/<model("student.student"):student_id>'], type="http", auth='user', website=True)
	def AdmissionFormView(self, student_id, **kw):
		print("Education Form View Controller has been called .........")
		admission_obj = request.env['student.admission']
		admission = admission_obj.search([('grno', '=', student_id.grno)])
		vals = {'admission' : admission, 'page_name' : 'student_admissions_form', 'user': request.env.user}
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", vals)
		return request.render("web_portal.student_admissions_form_template", vals)

	@http.route(['/my/assignment/<model("student.student"):student_id>'], type="http", auth='user', website=True)
	def AssignmentListView(self, student_id, **kw):
		students = request.env['student.student'].sudo().search([('user_id', '=', request.uid)], limit=1)
		print("STUDENT   IDDDDDDDDDD ", students, students.id)

		teacher_assignments = request.env['school.teacher.assignment'].sudo().search([
																					('standard_id', '=', students.standard_id.id),
																					('division_id', '=', students.division_id.id),
																					('state', '=', 'active')])
		print(">>>>>>>>>>>",teacher_assignments)
		# student_assignments = request.env['school.student.assignment'].sudo().search([('student_id', '=', students.id),
		# 																			  ('teacher_assignment_id', 'in', teacher_assignments.ids)])

		# print("::::::::::::::::::::", student_assignments)
		vals = {
				'student': students,
				'student_id': student_id,
				# 'student_assignments': student_assignments,
				'teacher_assignments': teacher_assignments,
				'page_name': 'assignment_list_view',
				'user': request.env.user,
				}
		return request.render("web_portal.assignment_list_view_portal", vals)

		# /my/submit_assignment

	@http.route([
		'/my/submit_assignment/<model("school.teacher.assignment"):student_id>'], type="http", auth='user', website=True, csrf=False)
	def SubmitAssignmentFormView(self, student_id, **kw):
		print("Submit Assignment Form View Controller has been called .........")
		print("---------------", student_id, student_id.id)

		student = request.env['student.student'].sudo().search([('user_id', '=', request.uid)], limit=1)
		student_assignments = request.env['school.student.assignment'].sudo().search([('student_id', '=', student.id)])
		teacher_assignments = request.env['school.teacher.assignment'].sudo().search([
																					('id', '=', student_id.id),
																					('standard_id', '=', student.standard_id.id),
																					('division_id', '=', student.division_id.id),
																					('state', '=', 'active')])
		
		if request.httprequest.method == 'POST':
		# Get the form data
			print(">>>>>>>>>>>><<<<<<<<<<<<<<<<<<", kw, request.httprequest.form)
			assignment_id = request.httprequest.form.get('teacher_assignments')
			file_format = request.httprequest.form.get('file_format')
			file_data = request.httprequest.files.get('file_data')
			print(">>>>>>>>>>>>>>>>file data<<<<<<", file_data)
			if file_data:
				file_name = file_data
				file_content = file_data.read()

				file_content_base64 = base64.b64encode(file_content)
				# file_content_str = file_content.decode('utf-8')
				# attachment = request.env['ir.attachment'].create({
				# 	'name': file_name,
				# 	'datas': file_content,
				# 	'datas_fname': file_name,
				# })
			print("ATTACHMENTSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",file_content_base64)
			assignment_obj = request.env['school.student.assignment'].sudo()
			vals = {
					'teacher_assignment_id': student_id.id,
					'teacher_id': student_id.teacher_id.id ,
					'subject_id': student_id.subject_id.id,
					'standard_id': student_id.standard_id.id,
					'division_id': student.division_id.id,
					'assign_date': student_id.assign_date,
					'due_date': student_id.due_date,
					'submission_type' : student_id.submission_type,
					'student_id': student.id,
					'attachfile_format': 'pdf',
					'file_name': file_name,
					'submit_assign': file_content_base64,
					'state' : 'active'
				}
			print("      VALSSSSSSS         ", vals)
			# check for old data
			search_domain = [('teacher_assignment_id', '=', student_id.id),('student_id', '=', student.id)]
			print("search_domain",search_domain)
			old_ids = assignment_obj.search(search_domain, limit=1)
			print(":::::OLD IDS:::::",old_ids)
			print("assignment_obj",assignment_obj)
			if old_ids:
				res = old_ids.write(vals)
				if res:
					vals = {
						'res': old_ids,
						'page_name' : 'assignment_submitted', 
						'user': request.env.user
					}
					return request.render("web_portal.assignment_submitted_portal", vals)
			else:

				res = request.env['school.student.assignment'].sudo().create(vals)
				print(":::::::::::::::::::::::::::::::::::::::::::", res, res.id)
				if res:
					vals = {
						'res': res,
						'page_name' : 'assignment_submitted', 
						'user': request.env.user
					}
					return request.render("web_portal.assignment_submitted_portal", vals)
			

		print("================",teacher_assignments)
		vals = {'student': student_id,
				'students' : student,
				'student_assignments': student_assignments,
				'teacher_assignments': teacher_assignments,
				'page_name' : 'submit_assignment_form_view', 
				'user': request.env.user}
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", vals)
		return request.render("web_portal.submit_assignment_form_view_portal", vals)


	@http.route([
		'/my/result/<model("student.marksheet.line"):student_id>'], type="http", auth='user', website=True)
	def ResultFormView(self, student_id, **kw):
		print("Education Form View Controller has been called .........")
		student = request.env['student.student'].sudo().search([('user_id', '=', request.uid)], limit=1)
		result_obj = request.env['student.result.line']
		print("REsULT LINE IDS", student_id.result_line_ids.ids, student_id.result_line_ids)
		result = result_obj.search([('student_id', '=', student.id),
									('id', 'in', student_id.result_line_ids.ids)])
		vals = {'student' : student_id, 'page_name' : 'student_result_form', 'user': request.env.user}
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", vals)
		return request.render("web_portal.student_result_form_template", vals)
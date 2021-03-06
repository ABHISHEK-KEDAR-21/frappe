# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals

import frappe, unittest
from frappe.desk.form.load import getdoctype, getdoc
from frappe.core.page.permission_manager.permission_manager import update, reset
from frappe.permissions import get_valid_perms

class TestFormLoad(unittest.TestCase):
	def test_load(self):
		getdoctype("DocType")
		meta = list(filter(lambda d: d.name=="DocType", frappe.response.docs))[0]
		self.assertEqual(meta.name, "DocType")
		self.assertTrue(meta.get("__js"))

		frappe.response.docs = []
		getdoctype("Event")
		meta = list(filter(lambda d: d.name=="Event", frappe.response.docs))[0]
		self.assertTrue(meta.get("__calendar_js"))

	def test_fieldlevel_permissions_in_load(self):
		user = frappe.get_doc('User', 'test@example.com')
		user.remove_roles('Website Manager')
		user.add_roles('Blogger')
		reset('Blog Post')

		frappe.db.set_value('DocField', {
			'fieldname': 'published',
			'parent': 'Blog Post'
		}, 'permlevel', 1)

		update('Blog Post', 'Website Manager', 0, 'permlevel', 1)

		frappe.set_user(user.name)

		# print frappe.as_json(get_valid_perms('Blog Post'))

		frappe.clear_cache(doctype='Blog Post')

		blog = frappe.db.get_value('Blog Post', {'title': '_Test Blog Post'})

		getdoc('Blog Post', blog)

		checked = False

		for doc in frappe.response.docs:
			if doc.name == blog:
				self.assertEqual(doc.published, None)
				checked = True

		self.assertTrue(checked, True)

		frappe.db.set_value('DocField', {
			'fieldname': 'published',
			'parent': 'Blog Post'
		}, 'permlevel', 0)

		reset('Blog Post')

		frappe.clear_cache(doctype='Blog Post')

		frappe.response.docs = []
		getdoc('Blog Post', blog)

		checked = False

		for doc in frappe.response.docs:
			if doc.name == blog:
				self.assertEqual(doc.published, 1)
				checked = True

		self.assertTrue(checked, True)

		frappe.set_user('Administrator')

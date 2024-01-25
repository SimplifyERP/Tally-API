// Copyright (c) 2023, saadchaudhary646@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tally Sales Invoice', {
	refresh: function(frm) {

		frm.set_query('sales_invoice', () => {
			return {
				filters: {
					docstatus: 1
				}
			}
		})
	},

	customer:function(frm) {

		frm.set_query('sales_invoice', () => {
			return {
				filters: {
					docstatus: 1,
					customer:cur_frm.doc.customer
				}
			}
		})
	},
});

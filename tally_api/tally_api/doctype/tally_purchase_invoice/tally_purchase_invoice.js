// Copyright (c) 2023, saadchaudhary646@gmail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Tally Purchase Invoice', {
	refresh: function(frm) {

		frm.set_query('purchase_invoice', () => {
			return {
				filters: {
					docstatus: 1
				}
			}
		})
	},

	supplier:function(frm) {

		frm.set_query('purchase_invoice', () => {
			return {
				filters: {
					docstatus: 1,
					supplier:cur_frm.doc.supplier
				}
			}
		})
	},
});

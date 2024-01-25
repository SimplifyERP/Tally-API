# Copyright (c) 2023, saadchaudhary646@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class TallySalesInvoice(Document):
	def before_submit(self):
		sd=self.from_date
		ed=self.to_date
		condition= ""
		if self.sales_invoice:
			condition = f"and si.name = '{self.sales_invoice}'"
		dd = frappe.db.sql(f""" 
				select 
					"Create" as VoucherAction, 
					DATE_FORMAT(si.posting_date, '%e-%b-%y') AS VoucherDate, 
					si.customer as Customer,
					sii.parent as VoucherNo, 
					sii.item_code as Item, 
					sii.gst_hsn_code as hsn_code,
					CONVERT(ROUND(CAST(sii.qty AS DECIMAL(10,2)), 2), CHAR) as Qty, 
					CONVERT(ROUND(CAST(CONVERT(sii.discount_percentage, CHAR) AS DECIMAL(10,2)), 2), CHAR) as DisPer, 
					sii.stock_uom as UOM, 
					CONVERT(ROUND(CAST(sii.amount AS DECIMAL(10,2)), 2) , CHAR)as ItemAmt,
					Null as CessPer,
					si.company as TallyCompany,
					CONVERT(ROUND(CAST(si.total AS DECIMAL(10,2)), 2), CHAR)  as total,
					CONVERT(ROUND(CAST(si.total_taxes_and_charges AS DECIMAL(10,2)), 2), CHAR)  as total_taxes_and_charges,
					CONVERT(ROUND(CAST(si.grand_total AS DECIMAL(10,2)), 2), CHAR)  as grand_total,
					address.name as address_name,
					address.address_title as address_title,
					address.address_line1 as address_line1,
					address.address_line2 as address_line2,
					address.city as city,
					address.county as county,
					address.state as state,
					address.state_code as state_code,
					address.country as country,
					address.country_code as country_code,
					address.pincode as pincode,
					address.email_id as email_id,
					address.phone as phone,
					address.gstin as gstin,
					address.gst_state as gst_state,
					address.gst_state_number as gst_state_number

				from 
					`tabSales Invoice Item` sii 
					left join `tabSales Invoice` si on sii.parent = si.name 
					left join  `tabAddress` address on address.name = si.customer_address 
						where 
							si.docstatus = 1  and si.posting_date between '{sd}' and '{ed}' {condition}
					""",as_dict=1)  

		for i in dd:
			taxes_and_charges = frappe.db.get_value('Sales Invoice', i.VoucherNo,'taxes_and_charges')

			tax_type = ("test","qweqwe")
			if  taxes_and_charges != None:
				if "In-state" in taxes_and_charges and taxes_and_charges != None:
					tax_type=('Output Tax SGST - VPS','Output Tax CGST - VPS')
				if "Out-state" in taxes_and_charges and taxes_and_charges != None:
					tax_type=('Output Tax IGST - VPS')
				
				taxes = frappe.db.sql(f"""  select CONVERT(ROUND(CAST(sum(stc.rate) AS DECIMAL(10,2)), 2), CHAR)  as rate from `tabSales Taxes and Charges` stc where stc.parent = '{i.VoucherNo}'  and stc.account_head in {tax_type}  """,as_dict=1)
				
				if len(taxes) >=1:
					i['GSTPer'] = taxes[0]['rate']
			else:
				i['GSTPer'] = 0

		self.output =str(json.dumps({"Inventories":dd}))
		frappe.db.commit()




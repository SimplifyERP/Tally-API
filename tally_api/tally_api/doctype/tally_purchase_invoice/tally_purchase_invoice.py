# Copyright (c) 2023, saadchaudhary646@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

class TallyPurchaseInvoice(Document):
	def before_submit(self):
		sd=self.from_date
		ed=self.to_date
		condition= ""
		if self.purchase_invoice:
			condition = f"and pi.name = '{self.purchase_invoice}'"
		dd = frappe.db.sql(f""" 
				select 
					"Create" as VoucherAction, 
					DATE_FORMAT(pi.posting_date, '%e-%b-%y') AS VoucherDate, 
					pi.supplier as Supplier,
					pii.parent as VoucherNo, 
					pii.item_code as Item, 
					pii.gst_hsn_code as hsn_code,
					CONVERT(ROUND(CAST(pii.qty AS DECIMAL(10,2)), 2), CHAR) as Qty, 
					CONVERT(ROUND(CAST(CONVERT(pii.discount_percentage, CHAR) AS DECIMAL(10,2)), 2), CHAR) as DisPer, 
					pii.stock_uom as UOM, 
					CONVERT(ROUND(CAST(pii.amount AS DECIMAL(10,2)), 2) , CHAR)as ItemAmt,
					Null as CessPer,
					pi.company as TallyCompany,
					CONVERT(ROUND(CAST(pi.total AS DECIMAL(10,2)), 2), CHAR)  as total,
					CONVERT(ROUND(CAST(pi.total_taxes_and_charges AS DECIMAL(10,2)), 2), CHAR)  as total_taxes_and_charges,
					CONVERT(ROUND(CAST(pi.grand_total AS DECIMAL(10,2)), 2), CHAR)  as grand_total,
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
					`tabPurchase Invoice Item` pii 
					left join `tabPurchase Invoice` pi on pii.parent = pi.name 
					left join  `tabAddress` address on address.name = pi.supplier_address 
						where 
							pi.docstatus = 1  and pi.posting_date between '{sd}' and '{ed}' {condition}
					""",as_dict=1)  

		for i in dd:
			taxes_and_charges = frappe.db.get_value('Purchase Invoice', i.VoucherNo,'taxes_and_charges')

			tax_type = ("test","qweqwe")
			if  taxes_and_charges != None:
				if "In-state" in taxes_and_charges and taxes_and_charges != None:
					tax_type=('Output Tax SGST - VPS','Output Tax CGST - VPS')
				if "Out-state" in taxes_and_charges and taxes_and_charges != None:
					tax_type=('Output Tax IGST - VPS')
				
				taxes = frappe.db.sql(f"""  select CONVERT(ROUND(CAST(sum(stc.rate) AS DECIMAL(10,2)), 2), CHAR)  as rate from `tabPurchase Taxes and Charges` stc where stc.parent = '{i.VoucherNo}'  and stc.account_head in {tax_type}  """,as_dict=1)
				
				if len(taxes) >=1:
					i['GSTPer'] = taxes[0]['rate']
			else:
				i['GSTPer'] = 0

		self.output =str(json.dumps({"Inventories":dd}))
		frappe.db.commit()




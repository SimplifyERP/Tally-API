import frappe
from frappe.model.document import Document
import json


@frappe.whitelist(allow_guest=True)
def tally_data():
    data = json.loads(frappe.request.data)
    # return data
    sd=data.get("from_date")
    ed=data.get("to_date")

    condition= ""
    if data.get("sales_invoice"):
        condition =  condition + f"""and si.name = '{data.get("sales_invoice")}'"""
    if data.get("customer"):
        condition  = condition + f"""and si.customer = '{data.get("customer")}'"""
    if data.get("company"):
        condition  = condition + f"""and si.company = '{data.get("company")}'"""


    dd = frappe.db.sql(f""" 
            select 
                "Create" as VoucherAction, 
                DATE_FORMAT(si.posting_date, '%e-%b-%y') AS VoucherDate, 
                si.customer as Customer,
                si.customer_name as CustomerName,
                sii.parent as VoucherNo, 
                sii.item_code as Item, 
                sii.gst_hsn_code as hsn_code,
                CONVERT(ROUND(CAST(sii.qty AS DECIMAL(10,2)), 2), CHAR) as Qty, 
                CONVERT(ROUND(CAST(CONVERT(sii.discount_percentage, CHAR) AS DECIMAL(10,2)), 2), CHAR) as DisPer, 
                sii.stock_uom as UOM, 
                    CONVERT(ROUND(CAST(sii.rate AS DECIMAL(10,2)), 2) , CHAR)as ItemAmt,

                CONVERT(ROUND(CAST(sii.sa_tax_rate AS DECIMAL(10,2)), 2) , CHAR)as ItemTaxPercentage,
                Null as CessPer,
                si.company as TallyCompany,
                si.discount_amount as DiscountAmount,
                CONVERT(ROUND(CAST(sii.amount AS DECIMAL(10,2)), 2), CHAR)  as total,

                CONVERT(ROUND(CAST((sii.sa_tax_amount) AS DECIMAL(10,2)), 2), CHAR)  as total_taxes_and_charges,

                CONVERT(ROUND(CAST(si.net_total AS DECIMAL(10,2)), 2), CHAR)  as grand_total,
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

                # CONVERT(ROUND(CAST(si.total_taxes_and_charges AS DECIMAL(10,2)), 2), CHAR)  as total_taxes_and_charges,


    # for i in dd:
    #     taxes_and_charges = frappe.db.get_value('Sales Invoice', i.VoucherNo,'taxes_and_charges')

    #     tax_type = ("test","qweqwe")
    #     if  taxes_and_charges != None:
    #         if "In-state" in taxes_and_charges and taxes_and_charges != None:
    #             tax_type=('Output Tax SGST - VPS','Output Tax CGST - VPS')
    #         if "Out-state" in taxes_and_charges and taxes_and_charges != None:
    #             tax_type=('Output Tax IGST - VPS')
            
    #         taxes = frappe.db.sql(f"""  select CONVERT(ROUND(CAST(sum(stc.rate) AS DECIMAL(10,2)), 2), CHAR)  as rate from `tabSales Taxes and Charges` stc where stc.parent = '{i.VoucherNo}'  and stc.account_head in {tax_type}  """,as_dict=1)
            
    #         if len(taxes) >=1:
    #             i['GSTPer'] = taxes[0]['rate']
    #     else:
    #         i['GSTPer'] = str(0)

    return json.loads(json.dumps({"Inventories":dd}))

@frappe.whitelist(allow_guest=True)
def purchase_tally_data():
    data = json.loads(frappe.request.data)
    # return data
    sd=data.get("from_date")
    ed=data.get("to_date")
    condition= ""
    if data.get("purchase_invoice"):
        condition =  condition + f"""and pi.name = '{data.get("purchase_invoice")}'"""
    if data.get("supplier"):
        condition  = condition + f"""and pi.supplier = '{data.get("supplier")}'"""
    dd = frappe.db.sql(f""" select
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


					CONVERT(ROUND(CAST((pii.amount + (pii.amount * 0.18)) AS DECIMAL(10,2)), 2), CHAR)  as total_taxes_and_charges,


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

					# CONVERT(ROUND(CAST(pi.total_taxes_and_charges AS DECIMAL(10,2)), 2), CHAR)  as total_taxes_and_charges,

    # for i in dd:
    #     taxes_and_charges = frappe.db.get_value('Purchase Invoice', i.VoucherNo,'taxes_and_charges')

    #     tax_type = ("test","qweqwe")
    #     if  taxes_and_charges != None:
    #         if "In-state" in taxes_and_charges and taxes_and_charges != None:
    #             tax_type=('Output Tax SGST - VPS','Output Tax CGST - VPS')
    #         if "Out-state" in taxes_and_charges and taxes_and_charges != None:
    #             tax_type=('Output Tax IGST - VPS')
            
    #         taxes = frappe.db.sql(f"""  select CONVERT(ROUND(CAST(sum(stc.rate) AS DECIMAL(10,2)), 2), CHAR)  as rate from `tabPurchase Taxes and Charges` stc where stc.parent = '{i.VoucherNo}'  and stc.account_head in {tax_type}  """,as_dict=1)
            
    #         if len(taxes) >=1:
    #             i['GSTPer'] = taxes[0]['rate']
    #     else:
    #         i['GSTPer'] = 0
    return json.loads(json.dumps({"Inventories":dd}))


@frappe.whitelist(allow_guest=True)
def tally_data_PaymentCredit():
    data = json.loads(frappe.request.data)
    sd=data.get("from_date")
    ed=data.get("to_date")
    condition= ""
    if data.get("name"):
        condition  = condition + f"""and pe.name  = "{data.get('name')}" """

    dd = frappe.db.sql(f""" 
                      
                    select 
                      "Create" as VoucherAction, 
                      "Payment" as VoucherType, 
                      pe.name as VoucherID,
                      DATE_FORMAT( pe.posting_date, '%e-%b-%y') as VoucherDate,
                      pe.party_name as LedgerName,
                      CONVERT(ROUND(CAST(pe.paid_amount AS DECIMAL(10,2)), 2), CHAR)as Amount,

                      pe.payment_type as payment_type,
                      pe.mode_of_payment as mode_of_payment,
                      pe.party_bank_account as bank_account,



                      pe.reference_no as ChequeNo,
                      DATE_FORMAT( pe.reference_date, '%e-%b-%y') as ChequeDate,
                      Null as Narration,
                      CONVERT(DAY( pe.posting_date), CHAR) as Day,
                      CONVERT(MONTH( pe.posting_date), CHAR) as MONTH,
                      CONVERT(YEAR( pe.posting_date), CHAR) as YEAR,

                      pe.company  as TallyCompany
                      
                    from 
                      `tabPayment Entry` pe

                    where pe.payment_type = "Receive"
                     and pe.posting_date between '{sd}' and '{ed}'  {condition}
                    
                    group by pe.name
                     order by pe.name 
                     
                                """,as_dict=1)  

    return json.loads(json.dumps({"PaymentCredit":dd}))




@frappe.whitelist(allow_guest=True)
def tally_data_PaymentDebit():
    data = json.loads(frappe.request.data)
    sd=data.get("from_date")
    ed=data.get("to_date")
    condition= ""
    if data.get("name"):
        condition  = condition + f"""and pe.name  = '{data.get("name")}'"""

    dd = frappe.db.sql(f""" 
                       
                    select 
                      "Create" as VoucherAction, 
                      "Payment" as VoucherType, 
                      pe.name as VoucherID,
                      DATE_FORMAT( pe.posting_date, '%e-%b-%y') as VoucherDate,
                      pe.party_name as LedgerName,

                      pe.mode_of_payment as mode_of_payment,
                      pe.party_bank_account as bank_account,

                      CONVERT(ROUND(CAST(pe.paid_amount AS DECIMAL(10,2)), 2), CHAR)as Amount,

                      pe.payment_type as payment_type,
                      per.reference_name as BillNo,
                      per.total_amount as  BillAmt,
                      pe.reference_no as ChequeNo,
                      DATE_FORMAT( pe.reference_date, '%e-%b-%y') as ChequeDate,
                      Null as Narration,  

                      CONVERT(DAY( pe.posting_date), CHAR) as Day,
                      CONVERT(MONTH( pe.posting_date), CHAR) as MONTH,
                      CONVERT(YEAR( pe.posting_date), CHAR) as YEAR,

                      pe.company  as TallyCompany
                      
                    from 
                      `tabPayment Entry` pe
                    left join `tabPayment Entry Reference` per on per.parent = pe.name
                      
                    where pe.payment_type = "Pay" 
                    and pe.posting_date between '{sd}' and '{ed}' {condition}
                    
                    group by pe.name
                     order by pe.name

                                """,as_dict=1)  

    return json.loads(json.dumps({"PaymentDebit":dd}))






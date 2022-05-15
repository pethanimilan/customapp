import frappe, json
from frappe.utils.file_manager import save_file

@frappe.whitelist(allow_guest=False, methods=["POST"])
def GetSalesInvoiceDetails():
    """
        This API Will be Used to Get the Sales Invoice Details Along with Item Details
    """
    
    data = json.loads(frappe.request.data)
    filters = {"docstatus":1}
    
    if data.get("status"):
        status_filter = data.get('status')
        if isinstance(status_filter, str):
            filters.update({"status": status_filter})
        elif isinstance(status_filter, list):
            filters.update({"status":("in", status_filter)})
    
    si_list = frappe.get_all("Sales Invoice",filters, ['*'], order_by="posting_date DESC")
    si_item_list = frappe.get_all("Sales Invoice Item", {"docstatus":1}, ['*'], order_by = "idx")

    si_map = {}
    for item in si_item_list:
        if not si_map.get(item.parent):
            si_map[item.parent] = [item]
        else:
            si_map[item.parent].append(item)

    for si in si_list:
        if si_map.get(si.name):
            si.items = si_map.get(si.name)

    return {
        "status": True,
        "status_response": "Success" if si_list else "Empty Data",
        "data": si_list
    }


@frappe.whitelist(allow_guest=False, methods=["POST"])
def UploadFile():
    """
        This API Will be Used to Upload the Files to the particular Document
    """
    data = frappe.request.form
    file_list = frappe.request.files.getlist("file_details")
    dt = data.get("doctype")
    dn = data.get("docname")

    if not (file_list and dt and dn):
        return {
            "status":False,
            "status_response": "Please Provide File Details and Document Type and Document Name"
        }

    if not frappe.db.exists(dt, dn):
        return {
            "status": False, 
            "status_response":"Given Document Type and Name Combination Doesn't Exists."
        }


    for file_content_obj in file_list:
        if not file_content_obj:
            return {
                "status": False,
                "status_response": "Please Provide File Content."
            }

        content = file_content_obj.stream.read()

        file_doc = save_file(file_content_obj.filename, content, dt, dn, folder=None, decode=False, is_private=1)

    return {
        "status": True,
        "status_response": "File has been Uploaded Successfully"
    }
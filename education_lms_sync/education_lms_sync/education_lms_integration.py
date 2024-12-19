import frappe

def sync_course_to_lms(doc, method):
    """
    Sync Course creation from Education to LMS
    """
    # Check if the course already exists in LMS
    if not frappe.db.exists("LMS Course", {"course_name": doc.course_name}):
        lms_course = frappe.get_doc({
            "doctype": "LMS Course",
            "course_name": doc.course_name,
            "description": doc.description,
            "course_code": doc.course_code,
            "course_duration": doc.duration
        })
        lms_course.insert(ignore_permissions=True)
        frappe.msgprint(f"LMS Course '{doc.course_name}' created successfully.")
    else:
        frappe.msgprint(f"LMS Course '{doc.course_name}' already exists.")

def sync_student_to_lms(doc, method):
    """
    Sync Student Enrollment from Education to LMS
    """
    # Find the LMS Course
    lms_course = frappe.db.get_value("LMS Course", {"course_name": doc.course_name}, "name")

    if lms_course:
        # Check if the student is already enrolled
        if not frappe.db.exists("LMS Enrollment", {"student": doc.student, "course": lms_course}):
            # Create LMS Enrollment
            lms_enrollment = frappe.get_doc({
                "doctype": "LMS Enrollment",
                "student": doc.student,
                "course": lms_course,
                "enrollment_date": doc.enrollment_date
            })
            lms_enrollment.insert(ignore_permissions=True)
            frappe.msgprint(f"Student '{doc.student}' enrolled in LMS Course '{doc.course_name}'.")
        else:
            frappe.msgprint(f"Student '{doc.student}' is already enrolled in LMS Course '{doc.course_name}'.")
    else:
        frappe.msgprint(f"LMS Course '{doc.course_name}' not found. Please create the course first.", alert=True)


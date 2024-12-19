import frappe

# 1. Sync Program Enrollment to LMS Enrollment
def sync_program_enrollment_to_lms(doc, method):
    """
    Sync Program Enrollment from Education to LMS Enrollment.
    Triggered when a Program Enrollment is created in Education.
    """
    try:
        frappe.logger().info(f"[SYNC START] Program Enrollment: {doc.name}")

        # Step 1: Fetch student email directly from the Student doctype
        student_email = frappe.db.get_value("Student", doc.student, "student_email_id")  # Correct field name
        student_name = frappe.db.get_value("Student", doc.student, "student_name")

        if not student_email:
            frappe.logger().error(f"[EMAIL ERROR] No email found for Student '{doc.student}'")
            return

        frappe.logger().info(f"[STUDENT INFO] Email: {student_email}, Name: {student_name}")

        # Step 2: Iterate over courses in the Program Enrollment
        for course_doc in doc.courses:
            course_name = course_doc.course_name
            frappe.logger().info(f"[COURSE FOUND] Course: '{course_name}'")

            # Fetch LMS Course
            lms_course = frappe.db.get_value("LMS Course", {"title": course_name}, "name")
            if not lms_course:
                frappe.logger().error(f"[COURSE ERROR] LMS Course '{course_name}' not found.")
                continue

            # Check if the LMS Enrollment already exists
            if not frappe.db.exists("LMS Enrollment", {"member": student_email, "course": lms_course}):
                frappe.logger().info(f"[ENROLLING] Member '{student_email}' to Course '{lms_course}'")
                lms_enrollment = frappe.get_doc({
                    "doctype": "LMS Enrollment",
                    "course": lms_course,          # Link to LMS Course
                    "member": student_email,       # Email as member
                    "member_name": student_name,   # Optional: Full name
                    "member_username": student_email,  # Optional: Use email as username
                })
                lms_enrollment.insert(ignore_permissions=True)
                frappe.logger().info(f"[ENROLLMENT SUCCESS] '{student_email}' enrolled in '{lms_course}'.")
            else:
                frappe.logger().info(f"[ALREADY ENROLLED] '{student_email}' already enrolled in '{lms_course}'.")

        frappe.db.commit()

    except Exception as e:
        frappe.logger().error(f"[SYNC ERROR] {str(e)}")
        frappe.log_error(title="Error in Syncing Program Enrollment to LMS", message=str(e))


# 2. Sync LMS Course to Education Course
def sync_lms_course_to_education(doc, method):
    """
    Sync LMS Course creation to Education Course.
    Triggered when a Course is created in LMS.
    """
    try:
        if not frappe.db.exists("Course", {"course_name": doc.title}):
            education_course = frappe.get_doc({
                "doctype": "Course",
                "course_name": doc.title,
                "description": doc.get("description", ""),
            })
            education_course.insert(ignore_permissions=True)
            frappe.db.commit()
            frappe.logger().info(f"[COURSE CREATED] Course '{doc.title}' created in Education.")
    except Exception as e:
        frappe.logger().error(f"[SYNC COURSE ERROR] {str(e)}")
        frappe.log_error(title="Error in Syncing LMS Course to Education", message=str(e))


# 3. Remove Education Course when LMS Course is Deleted
def remove_education_course(doc, method):
    """
    Remove corresponding Course in Education when LMS Course is deleted.
    """
    try:
        education_course = frappe.db.get_value("Course", {"course_name": doc.title}, "name")
        if education_course:
            frappe.delete_doc("Course", education_course, force=True)
            frappe.db.commit()
            frappe.logger().info(f"[COURSE DELETED] Education Course '{education_course}' deleted.")
    except Exception as e:
        frappe.logger().error(f"[REMOVE COURSE ERROR] {str(e)}")
        frappe.log_error(title="Error in Removing Education Course", message=str(e))


# 4. Delete LMS Enrollment when Program Enrollment is Deleted
def delete_lms_enrollment(doc, method):
    """
    Delete LMS Enrollment for a student when Program Enrollment is deleted.
    Triggered when Program Enrollment is deleted in Education.
    """
    try:
        frappe.logger().info(f"[DELETE SYNC START] Program Enrollment: {doc.name}")

        # Step 1: Fetch student email directly from the Student doctype
        student_email = frappe.db.get_value("Student", doc.student, "student_email_id")  # Correct field name

        if not student_email:
            frappe.logger().error(f"[EMAIL ERROR] No email found for Student '{doc.student}'")
            return

        frappe.logger().info(f"[STUDENT INFO] Email: {student_email}")

        # Step 2: Iterate over courses in the Program Enrollment
        for course_doc in doc.courses:
            course_name = course_doc.course_name
            frappe.logger().info(f"[COURSE FOUND] Course: '{course_name}'")

            # Fetch LMS Course
            lms_course = frappe.db.get_value("LMS Course", {"title": course_name}, "name")
            if not lms_course:
                frappe.logger().error(f"[COURSE ERROR] LMS Course '{course_name}' not found.")
                continue

            # Check if LMS Enrollment exists and delete it
            lms_enrollment = frappe.db.get_value(
                "LMS Enrollment", {"member": student_email, "course": lms_course}, "name"
            )
            if lms_enrollment:
                frappe.logger().info(f"[DELETING ENROLLMENT] '{student_email}' from Course '{lms_course}'")
                frappe.delete_doc("LMS Enrollment", lms_enrollment, force=True)
                frappe.logger().info(f"[ENROLLMENT DELETED] '{student_email}' removed from '{lms_course}'.")
            else:
                frappe.logger().info(f"[NOT FOUND] LMS Enrollment not found for '{student_email}' in '{lms_course}'.")

        frappe.db.commit()

    except Exception as e:
        frappe.logger().error(f"[DELETE SYNC ERROR] {str(e)}")
        frappe.log_error(title="Error in Deleting LMS Enrollment", message=str(e))


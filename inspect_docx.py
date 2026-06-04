import docx

for filename in ["Employee_Data_Management_System_Report.docx", "Employee_Data_Management_System_Report_Updated.docx", "Employee_Data_and_Payroll_System_Report.docx"]:
    try:
        doc = docx.Document(filename)
        print(f"--- {filename} ---")
        for i, p in enumerate(doc.paragraphs):
            if "Database Schema" in p.text:
                print(f"Found heading at paragraph {i}: {p.text}")
    except Exception as e:
        print(f"Error opening {filename}: {e}")

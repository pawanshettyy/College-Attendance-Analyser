import pdfplumber
import re
import pandas as pd

def extract_attendance_data(pdf_file):
    """Extract attendance data from PDF file"""
    with pdfplumber.open(pdf_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    
    # Extract student info
    student_name_match = re.search(r'Self Attendance Report\s*:\s*([^(]+)', text)
    student_name = student_name_match.group(1).strip() if student_name_match else "Unknown"
    
    # Extract attendance data
    lines = text.split('\n')
    data = []
    
    # Find the start of the attendance table
    for i, line in enumerate(lines):
        if re.search(r'SrNo\s+Subject\s+Subject\s+Type\s+Present\s+Total', line):
            start_idx = i + 1
            break
    else:
        start_idx = 0
    
    # Extract subject rows until summary rows
    for i in range(start_idx, len(lines)):
        line = lines[i].strip()
        # Skip empty lines
        if not line:
            continue
            
        # Stop at summary rows (which typically start with "Theory", "Practical", etc.)
        if any(line.startswith(word) for word in ["Theory", "Practical", "Tutorial", "Total", "Note"]):
            break
            
        # Try to extract subject data
        # Pattern: number, subject name, type (TH/PR/TU), present, total, percentage
        parts = re.split(r'\s{2,}', line)
        
        if len(parts) >= 5:  # Need at least 5 parts for a valid row
            try:
                # Sometimes subject name and type are merged, so we need to split them
                subject_parts = []
                subject_type = ""
                
                for part in parts[1:-3]:  # Skip first (serial) and last 3 (present, total, percentage)
                    if part in ["TH", "PR", "TU", "ESH"]:
                        subject_type = part
                    else:
                        subject_parts.append(part)
                
                subject_name = " ".join(subject_parts).strip()
                
                # If we don't have a type yet, try to extract it from the data
                if not subject_type and len(parts) > 3:
                    type_match = re.search(r'\b(TH|PR|TU|ESH)\b', parts[-4])
                    if type_match:
                        subject_type = type_match.group(1)
                
                # Get present and total values
                present = int(parts[-3])
                total = int(parts[-2])
                
                # Only add if we have valid numbers
                if present >= 0 and total > 0:
                    data.append({
                        "Subject": subject_name,
                        "Type": subject_type,
                        "Present": present,
                        "Total": total,
                        "Percentage": round(present / total * 100, 2)
                    })
            except (ValueError, IndexError):
                # Skip invalid rows
                pass
    
    # Extract overall attendance
    overall_match = re.search(r'Total\s+(\d+)\s+(\d+)\s+([\d.]+)', text)
    overall = {
        "Present": int(overall_match.group(1)) if overall_match else sum(item["Present"] for item in data),
        "Total": int(overall_match.group(2)) if overall_match else sum(item["Total"] for item in data),
    }
    overall["Percentage"] = round(overall["Present"] / overall["Total"] * 100, 2) if overall["Total"] > 0 else 0
    
    return {
        "student_name": student_name,
        "subjects": data,
        "overall": overall
    }
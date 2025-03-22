import pdfplumber
import re
import pandas as pd
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_attendance_data(pdf_file):
    """
    Extract attendance data from PDF file with improved error handling and
    support for different PDF formats.
    
    Args:
        pdf_file: A file-like object containing the PDF
        
    Returns:
        dict: Dictionary with student_name, subjects list, and overall attendance
    """
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"
                    
        if not text.strip():
            logger.warning("No text could be extracted from the PDF")
            return _get_empty_result()
            
        # Extract student info with more flexible pattern matching
        student_name_patterns = [
            r'Self Attendance Report\s*:\s*([^(]+)',  # Common format
            r'Student\s*Name\s*:\s*([^(]+)',          # Alternative format
            r'Name\s*:\s*([^(]+)',                   # Simpler format
        ]
        
        student_name = "Unknown"
        for pattern in student_name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                student_name = match.group(1).strip()
                break
                
        # Extract attendance data with improved pattern matching
        lines = text.split('\n')
        data = []
        
        # Find the start of the attendance table with more flexible pattern matching
        start_patterns = [
            r'SrNo\s+Subject\s+Subject\s+Type\s+Present\s+Total',  # Common format
            r'Sr\.?\s*No\.?\s+Subject\s+.*Present\s+Total',        # Alternative format
            r'Subject\s+Type\s+Present\s+Total',                   # Simpler format
        ]
        
        start_idx = 0
        for pattern in start_patterns:
            for i, line in enumerate(lines):
                if re.search(pattern, line, re.IGNORECASE):
                    start_idx = i + 1
                    break
            if start_idx > 0:
                break
                
        # Extract subject rows using improved regex patterns
        for i in range(start_idx, len(lines)):
            line = lines[i].strip()
            # Skip empty lines
            if not line:
                continue
                
            # Stop at summary rows
            if any(re.match(r'^\s*(theory|practical|tutorial|total|note)\s*', line, re.IGNORECASE) for word in ["Theory", "Practical", "Tutorial", "Total", "Note"]):
                break
                
            # Try multiple patterns to extract subject data
            try:
                # First try splitting by multiple spaces
                parts = re.split(r'\s{2,}', line)
                
                # If that doesn't work well, try a more structured approach
                if len(parts) < 4:
                    # Look for patterns like: [number] [subject] [type] [present] [total] [percentage]
                    match = re.search(r'^\s*\d+\s+(.+?)\s+(TH|PR|TU|ESH)\s+(\d+)\s+(\d+)\s+([\d.]+)', line)
                    if match:
                        subject_name = match.group(1).strip()
                        subject_type = match.group(2).strip()
                        present = int(match.group(3))
                        total = int(match.group(4))
                        
                        data.append({
                            "Subject": subject_name,
                            "Type": subject_type,
                            "Present": present,
                            "Total": total,
                            "Percentage": round(present / total * 100, 2) if total > 0 else 0
                        })
                        continue
                
                # Process the parts from split by spaces method
                if len(parts) >= 5:
                    # Try to identify subject, type, present, total
                    subject_parts = []
                    subject_type = ""
                    
                    # Look for known subject types
                    for part in parts:
                        if re.match(r'^(TH|PR|TU|ESH)$', part.strip()):
                            subject_type = part.strip()
                            
                    # If we found a type, everything before it is the subject name
                    if subject_type:
                        type_index = parts.index(subject_type)
                        subject_parts = parts[1:type_index]  # Skip first part (serial number)
                        subject_name = " ".join(subject_parts).strip()
                        
                        # The next parts should be present and total
                        for j in range(type_index + 1, len(parts)):
                            if parts[j].strip().isdigit():
                                present = int(parts[j])
                                if j + 1 < len(parts) and parts[j + 1].strip().isdigit():
                                    total = int(parts[j + 1])
                                    
                                    data.append({
                                        "Subject": subject_name,
                                        "Type": subject_type,
                                        "Present": present,
                                        "Total": total,
                                        "Percentage": round(present / total * 100, 2) if total > 0 else 0
                                    })
                                    break
            except (ValueError, IndexError) as e:
                logger.debug(f"Error parsing line: {line}, Error: {str(e)}")
                # Skip invalid rows, but don't crash
                continue
        
        # Extract overall attendance with more flexible pattern matching
        overall_patterns = [
            r'Total\s+(\d+)\s+(\d+)\s+([\d.]+)',  # Common format
            r'Overall\s+(\d+)\s+(\d+)\s+([\d.]+)', # Alternative format
        ]
        
        overall = None
        for pattern in overall_patterns:
            match = re.search(pattern, text)
            if match:
                overall = {
                    "Present": int(match.group(1)),
                    "Total": int(match.group(2)),
                    "Percentage": float(match.group(3))
                }
                break
                
        # If no overall data found, calculate from subjects
        if not overall:
            total_present = sum(item["Present"] for item in data) if data else 0
            total_classes = sum(item["Total"] for item in data) if data else 0
            overall = {
                "Present": total_present,
                "Total": total_classes,
                "Percentage": round(total_present / total_classes * 100, 2) if total_classes > 0 else 0
            }
            
        return {
            "student_name": student_name,
            "subjects": data,
            "overall": overall
        }
        
    except Exception as e:
        logger.error(f"Error extracting attendance data: {str(e)}")
        logger.debug(traceback.format_exc())
        return _get_empty_result()
        
def _get_empty_result():
    """Return an empty result structure when extraction fails"""
    return {
        "student_name": "Unknown",
        "subjects": [],
        "overall": {
            "Present": 0,
            "Total": 0,
            "Percentage": 0
        }
    }
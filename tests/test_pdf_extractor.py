import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import io

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pdf_extractor import extract_attendance_data

class TestPDFExtractor(unittest.TestCase):
    
    @patch('pdfplumber.open')
    def test_extract_attendance_data_basic(self, mock_pdf_open):
        """Test basic extraction functionality"""
        # Mock PDF content
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = """
Self Attendance Report : PAWAN NARAYAN SHETTY FE - AIML -C 2024-2025(SEMESTER- II)
SrNo Subject Subject Type Present Total Period Percentage (%)
1 Physics TH 9 24 37.50
2 Mathematics - II TH 14 23 60.87
Theory 57 105 54.29
Practical 14 17 82.35
Tutorial 5 5 100
Total 76 127 59.84
        """
        mock_pdf.pages = [mock_page]
        mock_pdf_open.return_value.__enter__.return_value = mock_pdf
        
        # Test the function
        result = extract_attendance_data(io.BytesIO(b'dummy pdf content'))
        
        # Assertions
        self.assertEqual(result['student_name'], 'PAWAN NARAYAN SHETTY FE - AIML -C 2024-2025(SEMESTER- II)')
        self.assertEqual(len(result['subjects']), 2)  # Two subjects should be extracted
        
        # Check Physics subject
        physics = next(s for s in result['subjects'] if s['Subject'] == 'Physics')
        self.assertEqual(physics['Type'], 'TH')
        self.assertEqual(physics['Present'], 9)
        self.assertEqual(physics['Total'], 24)
        self.assertAlmostEqual(physics['Percentage'], 37.50, places=2)
        
        # Check Mathematics subject
        math = next(s for s in result['subjects'] if s['Subject'] == 'Mathematics - II')
        self.assertEqual(math['Type'], 'TH')
        self.assertEqual(math['Present'], 14)
        self.assertEqual(math['Total'], 23)
        self.assertAlmostEqual(math['Percentage'], 60.87, places=2)
        
        # Check overall attendance
        self.assertEqual(result['overall']['Present'], 76)
        self.assertEqual(result['overall']['Total'], 127)
        self.assertAlmostEqual(result['overall']['Percentage'], 59.84, places=2)
    
    @patch('pdfplumber.open')
    def test_extract_attendance_data_empty(self, mock_pdf_open):
        """Test extraction with empty or invalid PDF"""
        # Mock empty PDF content
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = ""
        mock_pdf.pages = [mock_page]
        mock_pdf_open.return_value.__enter__.return_value = mock_pdf
        
        # Test the function
        result = extract_attendance_data(io.BytesIO(b'dummy pdf content'))
        
        # Assertions
        self.assertEqual(result['student_name'], 'Unknown')
        self.assertEqual(len(result['subjects']), 0)  # No subjects should be extracted
        self.assertEqual(result['overall']['Present'], 0)
        self.assertEqual(result['overall']['Total'], 0)
        self.assertEqual(result['overall']['Percentage'], 0)

if __name__ == '__main__':
    unittest.main()
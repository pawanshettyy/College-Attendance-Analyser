import sys
import os
import unittest

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.attendance_calc import calculate_classes_needed, calculate_classes_can_miss

class TestAttendanceCalculations(unittest.TestCase):
    
    def test_classes_needed_already_above_target(self):
        """Test when current attendance is already above target"""
        current_present = 80
        current_total = 100
        target_percentage = 75.0
        
        result = calculate_classes_needed(current_present, current_total, target_percentage)
        self.assertEqual(result, 0, "Should return 0 when already above target")
        
    def test_classes_needed_below_target(self):
        """Test when current attendance is below target"""
        current_present = 70
        current_total = 100
        target_percentage = 75.0
        
        # Expected: (75*100 - 100*70) / (100 - 75) = (7500 - 7000) / 25 = 500 / 25 = 20
        # Ceiling of 20 is 20
        result = calculate_classes_needed(current_present, current_total, target_percentage)
        self.assertEqual(result, 20, "Should correctly calculate classes needed")
        
    def test_classes_needed_edge_case(self):
        """Test edge case with very low attendance"""
        current_present = 10
        current_total = 100
        target_percentage = 75.0
        
        # Expected: (75*100 - 100*10) / (100 - 75) = (7500 - 1000) / 25 = 6500 / 25 = 260
        # Ceiling of 260 is 260
        result = calculate_classes_needed(current_present, current_total, target_percentage)
        self.assertEqual(result, 260, "Should handle edge case correctly")
        
    def test_can_miss_already_below_target(self):
        """Test when current attendance is already below target"""
        current_present = 70
        current_total = 100
        target_percentage = 75.0
        upcoming_classes = 10
        
        result = calculate_classes_can_miss(current_present, current_total, target_percentage, upcoming_classes)
        self.assertEqual(result, 0, "Should return 0 when already below target")
        
    def test_can_miss_above_target(self):
        """Test when current attendance is above target"""
        current_present = 80
        current_total = 100
        target_percentage = 75.0
        upcoming_classes = 10
        
        # Future total = 110, future present = 90
        # Max skip = floor(90 - (75 * 110 / 100)) = floor(90 - 82.5) = floor(7.5) = 7
        result = calculate_classes_can_miss(current_present, current_total, target_percentage, upcoming_classes)
        self.assertEqual(result, 7, "Should correctly calculate classes that can be missed")
        
    def test_can_miss_exactly_at_target(self):
        """Test when current attendance is exactly at target"""
        current_present = 75
        current_total = 100
        target_percentage = 75.0
        upcoming_classes = 10
        
        # Future total = 110, future present = 85
        # Max skip = floor(85 - (75 * 110 / 100)) = floor(85 - 82.5) = floor(2.5) = 2
        result = calculate_classes_can_miss(current_present, current_total, target_percentage, upcoming_classes)
        self.assertEqual(result, 2, "Should correctly calculate classes that can be missed when exactly at target")

if __name__ == '__main__':
    unittest.main()
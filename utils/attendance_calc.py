import math

def calculate_classes_needed(current_present, current_total, target_percentage):
    """
    Calculate how many more classes need to be attended to reach the target percentage.
    
    Args:
        current_present (int): Number of classes currently attended
        current_total (int): Total number of classes held so far
        target_percentage (float): Target attendance percentage
        
    Returns:
        int: Number of consecutive classes needed to attend
    """
    if current_present / current_total * 100 >= target_percentage:
        return 0
    
    # Formula: (current_present + x) / (current_total + x) = target_percentage / 100
    # Solving for x: x = (target_percentage * current_total - 100 * current_present) / (100 - target_percentage)
    classes_needed = math.ceil((target_percentage * current_total - 100 * current_present) / (100 - target_percentage))
    
    return classes_needed

def calculate_classes_can_miss(current_present, current_total, target_percentage, upcoming_classes=10):
    """
    Calculate how many classes can be missed while maintaining target percentage.
    
    Args:
        current_present (int): Number of classes currently attended
        current_total (int): Total number of classes held so far
        target_percentage (float): Target attendance percentage to maintain
        upcoming_classes (int): Number of upcoming classes scheduled
        
    Returns:
        int: Number of classes that can be safely missed
    """
    # Current percentage
    current_percentage = (current_present / current_total) * 100
    
    # If already below target, can't miss any more
    if current_percentage < target_percentage:
        return 0
    
    # Calculate total after adding all upcoming classes
    future_total = current_total + upcoming_classes
    future_present = current_present + upcoming_classes
    
    # Calculate how many classes can be skipped while maintaining target
    # Formula: (future_present - x) / future_total >= target_percentage / 100
    # Solving for x: x <= future_present - (target_percentage * future_total / 100)
    max_skip = math.floor(future_present - (target_percentage * future_total / 100))
    
    # Cannot skip more than upcoming classes
    return min(max_skip, upcoming_classes)
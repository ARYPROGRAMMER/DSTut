import json
import pandas as pd
from typing import Dict, List

def load_data() -> tuple:
    """Load all necessary data files with error handling"""
    try:
        # Load schedules
        with open('schedules.json', 'r') as f:
            schedules = json.load(f)
        
        # Load dataset
        sheets = pd.read_excel('dataset.xlsx', sheet_name=None)
        return schedules, sheets
    except FileNotFoundError as e:
        print(f"Error: Required file not found - {e}")
        return None, None
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in schedules.json")
        return None, None

def check_time_conflicts(schedules: Dict) -> List[str]:
    """Check for student time conflicts"""
    conflicts = []
    for student_id, schedule in schedules['student'].items():
        time_blocks = {}
        for class_info in schedule:
            block = class_info['block']
            if block in time_blocks:
                conflicts.append(f"Student {student_id} has conflict in block {block}: "
                               f"{time_blocks[block]} vs {class_info['course']}")
            time_blocks[block] = class_info['course']
    return conflicts

def check_room_capacity(schedules: Dict, rooms_df: pd.DataFrame) -> List[str]:
    """Validate room capacity constraints"""
    violations = []
    room_capacities = dict(zip(rooms_df['Room'], rooms_df['Capacity']))
    
    # Create room occupancy dictionary
    room_occupancy = {}
    for student_schedule in schedules['student'].values():
        for class_info in student_schedule:
            if 'room' not in class_info:
                violations.append(f"Missing room assignment in schedule")
                continue
                
            key = f"{class_info['room']}_{class_info['block']}"
            if class_info['room'] not in room_capacities:
                violations.append(f"Invalid room assignment: {class_info['room']}")
                continue
                
            room_occupancy[key] = room_occupancy.get(key, 0) + 1
    
    # Check for violations
    for key, count in room_occupancy.items():
        room, block = key.split('_')
        if room in room_capacities and count > room_capacities[room]:
            violations.append(f"Room {room} exceeded capacity in block {block}: "
                            f"{count} > {room_capacities[room]}")
    
    return violations

def check_section_capacity(schedules: Dict, courses_df: pd.DataFrame) -> List[str]:
    """Validate section capacity constraints"""
    violations = []
    section_counts = {}
    
    # Count students in each section
    for schedule in schedules['student'].values():
        for class_info in schedule:
            section_key = f"{class_info['course']}_{class_info['section']}"
            section_counts[section_key] = section_counts.get(section_key, 0) + 1
    
    # Check against max_size
    for course_row in courses_df.itertuples():
        course_sections = [key for key in section_counts.keys() 
                         if key.startswith(f"{course_row.Course}_")]
        for section_key in course_sections:
            if section_counts[section_key] > course_row.Max_Size:
                violations.append(f"Section {section_key} exceeded capacity: "
                               f"{section_counts[section_key]} > {course_row.Max_Size}")
    
    return violations

def check_teacher_conflicts(schedules: Dict) -> List[str]:
    """Check for teacher schedule conflicts"""
    conflicts = []
    teacher_blocks = {}
    
    for student_schedule in schedules['student'].values():
        for class_info in student_schedule:
            key = f"{class_info['teacher']}_{class_info['block']}"
            course_section = f"{class_info['course']}_{class_info['section']}"
            
            if key in teacher_blocks and teacher_blocks[key] != course_section:
                conflicts.append(f"Teacher {class_info['teacher']} has conflict in block "
                               f"{class_info['block']}: {teacher_blocks[key]} vs {course_section}")
            teacher_blocks[key] = course_section
    
    return conflicts

def check_teacher_workload(schedules: Dict, lecturers_df: pd.DataFrame) -> List[str]:
    """Validate teacher workload constraints"""
    violations = []
    teacher_blocks = {}
    
    # Count teaching blocks per teacher
    for student_schedule in schedules['student'].values():
        for class_info in student_schedule:
            if 'teacher' not in class_info:
                continue
                
            teacher = class_info['teacher']
            course_section = f"{class_info['course']}_{class_info['section']}"
            
            if teacher not in teacher_blocks:
                teacher_blocks[teacher] = set()
            teacher_blocks[teacher].add(f"{course_section}_{class_info['block']}")
    
    # Check workload limits
    for teacher, blocks in teacher_blocks.items():
        if len(blocks) > 5:  # Assuming max 5 blocks per teacher
            violations.append(f"Teacher {teacher} exceeds maximum workload: {len(blocks)} blocks")
    
    return violations

def validate_schedule_format(schedules: Dict) -> List[str]:
    """Validate the format of the schedule data"""
    errors = []
    required_keys = ['student', 'stats']
    required_class_info = ['course', 'section', 'block', 'room', 'teacher']
    
    # Check main structure
    for key in required_keys:
        if key not in schedules:
            errors.append(f"Missing required key: {key}")
    
    # Validate student schedule format
    if 'student' in schedules:
        for student_id, schedule in schedules['student'].items():
            if not isinstance(schedule, list):
                errors.append(f"Invalid schedule format for student {student_id}")
                continue
            
            for class_info in schedule:
                missing_fields = [field for field in required_class_info 
                                if field not in class_info]
                if missing_fields:
                    errors.append(f"Student {student_id} missing fields: {missing_fields}")
    
    return errors

def evaluate_solution():
    """Main evaluation function"""
    schedules, sheets = load_data()
    if not schedules or not sheets:
        return
    
    print("\n=== Schedule Evaluation ===")
    
    # Validate schedule format
    format_errors = validate_schedule_format(schedules)
    if format_errors:
        print("\nSchedule Format Errors:")
        for error in format_errors:
            print(f"- {error}")
        return  # Stop evaluation if format is invalid
    
    # 1. Time conflict check
    time_conflicts = check_time_conflicts(schedules)
    print(f"\nTime Conflicts: {len(time_conflicts)}")
    if time_conflicts:
        print("Sample conflicts:")
        for conflict in time_conflicts[:5]:
            print(f"- {conflict}")
    
    # 2. Room capacity check
    room_violations = check_room_capacity(schedules, sheets['Room list'])
    print(f"\nRoom Capacity Violations: {len(room_violations)}")
    if room_violations:
        print("Sample violations:")
        for violation in room_violations[:5]:
            print(f"- {violation}")
    
    # 3. Section capacity check
    section_violations = check_section_capacity(schedules, sheets['Course list'])
    print(f"\nSection Capacity Violations: {len(section_violations)}")
    if section_violations:
        print("Sample violations:")
        for violation in section_violations[:5]:
            print(f"- {violation}")
    
    # 4. Teacher conflict check
    teacher_conflicts = check_teacher_conflicts(schedules)
    print(f"\nTeacher Conflicts: {len(teacher_conflicts)}")
    if teacher_conflicts:
        print("Sample conflicts:")
        for conflict in teacher_conflicts[:5]:
            print(f"- {conflict}")
    
    # Add teacher workload check
    workload_violations = check_teacher_workload(schedules, sheets['Lecturer list'])
    
    # Print all results
    print(f"\nTotal Violations Found: {sum(len(x) for x in [time_conflicts, room_violations, section_violations, teacher_conflicts, workload_violations])}")
    
    # Print detailed statistics
    if any([time_conflicts, room_violations, section_violations, teacher_conflicts, workload_violations]):
        print("\nDetailed Violation Report:")
        print(f"Time Conflicts: {len(time_conflicts)}")
        print(f"Room Capacity Violations: {len(room_violations)}")
        print(f"Section Capacity Violations: {len(section_violations)}")
        print(f"Teacher Conflicts: {len(teacher_conflicts)}")
        print(f"Workload Violations: {len(workload_violations)}")
    else:
        print("\nNo violations found! Schedule is valid.")

if __name__ == "__main__":
    evaluate_solution() 
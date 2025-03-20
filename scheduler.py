from pulp import *
import pandas as pd
from typing import Dict, List
import logging

class CourseScheduler:
    def __init__(self, data_processor):
        self.processor = data_processor
        self.problem = LpProblem("Course_Scheduling", LpMaximize)
        self.time_blocks = self._generate_time_blocks()
        self.sections = {}
        self.assignments = {}
        self.valid_requests = []
        
    def _generate_time_blocks(self) -> List[str]:
        """Generate available time blocks based on rules"""
        # Using actual blocks from Excel
        blocks = ["1A", "1B", "2A", "2B", "3A", "3B", "4A", "4B"]
        return blocks
    
    def preprocess_requests(self):
        """Preprocess requests to ensure validity"""
        valid_courses = set(self.processor.courses.keys())
        self.valid_requests = []
        
        print("\nPreprocessing Requests:")
        print(f"Total courses available: {len(valid_courses)}")
        print("Sample course codes:", list(valid_courses)[:5])
        
        for request in self.processor.student_requests:
            course_code = request['course_code']
            if course_code in valid_courses:
                self.valid_requests.append(request)
            else:
                print(f"Skipping invalid course code: {course_code}")
        
        print(f"Total requests: {len(self.processor.student_requests)}")
        print(f"Valid requests: {len(self.valid_requests)}")
    
    def create_variables(self):
        """Create decision variables"""
        self.preprocess_requests()
        
        # Create section assignment variables
        for course_id, course in self.processor.courses.items():
            num_sections = int(course.get('Number of sections', 1))
            for section in range(num_sections):
                for block in self.time_blocks:
                    name = f"section_{course_id}_{section}_{block}"
                    self.sections[name] = LpVariable(name, cat='Binary')
        
        # Create student assignment variables
        for request in self.valid_requests:
            student_id = request['student_id']
            course_id = request['course_code']
            num_sections = int(self.processor.courses[course_id].get('Number of sections', 1))
            
            for section in range(num_sections):
                name = f"assign_{student_id}_{course_id}_{section}"
                self.assignments[name] = LpVariable(name, cat='Binary')
    
    def add_constraints(self):
        """Add scheduling constraints with relaxed conditions"""
        constraints_added = 0
        
        # 1. Time block conflicts (most important constraint)
        for student_id in set(r['student_id'] for r in self.valid_requests):
            for block in self.time_blocks:
                block_assignments = []
                student_courses = [r for r in self.valid_requests if r['student_id'] == student_id]
                
                for request in student_courses:
                    course_id = request['course_code']
                    num_sections = int(self.processor.courses[course_id].get('Number of sections', 1))
                    
                    for section in range(num_sections):
                        # Create a single variable for student-course-section-block assignment
                        var_name = f"assign_{student_id}_{course_id}_{section}_{block}"
                        self.assignments[var_name] = LpVariable(var_name, 0, 1, LpBinary)
                        block_assignments.append(self.assignments[var_name])
                
                if block_assignments:
                    # A student can't be in multiple courses in the same block
                    self.problem += lpSum(block_assignments) <= 1, f"block_{student_id}_{block}"
                    constraints_added += 1

        # 2. Section capacity constraints (relaxed)
        for course_id, course in self.processor.courses.items():
            max_size = int(course.get('Maximum section size', 30))
            num_sections = int(course.get('Number of sections', 1))
            
            for section in range(num_sections):
                section_students = []
                for request in self.valid_requests:
                    if request['course_code'] == course_id:
                        for block in self.time_blocks:
                            var_name = f"assign_{request['student_id']}_{course_id}_{section}_{block}"
                            if var_name in self.assignments:
                                section_students.append(self.assignments[var_name])
                
                if section_students:
                    # Allow 20% overflow in section size
                    self.problem += lpSum(section_students) <= max_size * 1.2, f"capacity_{course_id}_{section}"
                    constraints_added += 1

        # 3. Course assignment constraints (relaxed)
        for request in self.valid_requests:
            student_id = request['student_id']
            course_id = request['course_code']
            num_sections = int(self.processor.courses[course_id].get('Number of sections', 1))
            
            course_assignments = []
            for section in range(num_sections):
                for block in self.time_blocks:
                    var_name = f"assign_{student_id}_{course_id}_{section}_{block}"
                    if var_name in self.assignments:
                        course_assignments.append(self.assignments[var_name])
            
            if course_assignments:
                # Student should be assigned to at most one section of each course
                self.problem += lpSum(course_assignments) <= 1, f"one_section_{student_id}_{course_id}"
                constraints_added += 1

        print(f"Added {constraints_added} constraints")
    
    def set_objective(self):
        """Simplified objective function"""
        priority_weights = {
            'Core course': 100,
            'Required': 90,
            'Requested': 50,
            'Recommended': 25
        }
        
        objective_terms = []
        for request in self.valid_requests:
            student_id = request['student_id']
            course_id = request['course_code']
            priority = request.get('Priority', 'Requested')
            weight = priority_weights.get(priority, 50)
            
            for section in range(int(self.processor.courses[course_id].get('Number of sections', 1))):
                for block in self.time_blocks:
                    var_name = f"assign_{student_id}_{course_id}_{section}_{block}"
                    if var_name in self.assignments:
                        objective_terms.append(weight * self.assignments[var_name])
        
        self.problem += lpSum(objective_terms)
    
    def solve(self):
        """Create and solve the scheduling problem"""
        print("Creating variables...")
        self.create_variables()
        
        print("Adding constraints...")
        self.add_constraints()
        
        print("Setting objective function...")
        self.set_objective()
        
        print("Solving problem...")
        status = self.problem.solve()
        
        # Debug information
        print(f"\nProblem status: {LpStatus[status]}")
        print(f"Number of variables: {len(self.problem.variables())}")
        print(f"Number of constraints: {len(self.problem.constraints)}")
        
        return status == 1
    
    def generate_schedules(self):
        """Generate schedules from solution"""
        schedules = {
            'student': {},
            'teacher': {},  # Will populate this
            'room': {},     # Will populate this
            'stats': {
                'total_requests': len(self.processor.student_requests),
                'fulfilled_requests': 0,
                'priority_stats': {
                    'Core course': {'total': 0, 'fulfilled': 0},
                    'Required': {'total': 0, 'fulfilled': 0},
                    'Requested': {'total': 0, 'fulfilled': 0},
                    'Recommended': {'total': 0, 'fulfilled': 0}
                }
            }
        }

        # Count total requests by priority
        for request in self.valid_requests:
            priority = request.get('Priority', 'Requested')  # Case sensitive!
            if priority in schedules['stats']['priority_stats']:
                schedules['stats']['priority_stats'][priority]['total'] += 1

        # Process assignments
        for request in self.valid_requests:
            student_id = request['student_id']
            course_id = request['course_code']
            priority = request.get('Priority', 'Requested')
            
            # Check all possible assignments
            assigned = False
            for section in range(int(self.processor.courses[course_id].get('Number of sections', 1))):
                for block in self.time_blocks:
                    var_name = f"assign_{student_id}_{course_id}_{section}_{block}"
                    if var_name in self.assignments and value(self.assignments[var_name]) > 0.5:
                        # Initialize student schedule if needed
                        if student_id not in schedules['student']:
                            schedules['student'][student_id] = []
                        
                        # Find room assignment
                        room_id = None
                        for room in self.processor.rooms.keys():
                            if (self.processor.rooms[room]['course_code'] == course_id and 
                                self.processor.rooms[room]['section'] == str(section)):
                                room_id = room
                                break
                        
                        # Find teacher assignment
                        teacher_id = None
                        for lecturer_id, lecturer in self.processor.lecturers.items():
                            if lecturer['code'] == course_id:
                                teacher_id = lecturer_id
                                break
                        
                        # Record assignment
                        assignment = {
                            'course': course_id,
                            'section': section,
                            'block': block,
                            'room': room_id,
                            'teacher': teacher_id
                        }
                        
                        schedules['student'][student_id].append(assignment)
                        
                        # Update teacher schedule
                        if teacher_id:
                            if teacher_id not in schedules['teacher']:
                                schedules['teacher'][teacher_id] = []
                            schedules['teacher'][teacher_id].append(assignment)
                        
                        # Update room schedule
                        if room_id:
                            if room_id not in schedules['room']:
                                schedules['room'][room_id] = []
                            schedules['room'][room_id].append(assignment)
                        
                        # Update statistics
                        schedules['stats']['fulfilled_requests'] += 1
                        if priority in schedules['stats']['priority_stats']:
                            schedules['stats']['priority_stats'][priority]['fulfilled'] += 1
                        assigned = True
                        break
                if assigned:
                    break

        return schedules 
import pandas as pd
import json
from typing import Dict, List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        self.lecturers = {}
        self.rooms = {}
        self.courses = {}
        self.student_requests = []
        
    def clean_lecturer_data(self, df: pd.DataFrame) -> Dict:
        """Clean and structure lecturer data"""
        cleaned_data = {}
        
        # These are the actual column names from your Excel
        for _, row in df.iterrows():
            lecturer_id = str(row['Lecturer ID']).strip()
            cleaned_data[lecturer_id] = {
                'title': str(row['Lecture Title']).strip(),
                'code': str(row['lecture Code']).strip(),
                'length': str(row['Length']).strip(),
                'start_term': str(row['Start Term']).strip(),
                'section': str(row['Section number']).strip()
            }
        return cleaned_data

    def clean_room_data(self, df: pd.DataFrame) -> Dict:
        """Clean and structure room data"""
        cleaned_data = {}
        
        for _, row in df.iterrows():
            room_id = str(row['Room Number']).strip()
            cleaned_data[room_id] = {
                'course_title': str(row['Course Title']).strip(),
                'section': str(row['Section number']).strip(),
                'year': str(row[' Year']).strip(),  # Note the space before Year
                'term': str(row['Term Description']).strip(),
                'prof_id': str(row['prof ID']).strip(),
                'lecture_id': str(row['lecture ID']).strip(),
                'course_code': str(row['Course Code']).strip(),
                'course_length': str(row['Course Length']).strip(),
                'term_name': str(row['Term name']).strip()
            }
        return cleaned_data

    def clean_course_data(self, df: pd.DataFrame) -> Dict:
        """Clean and structure course data"""
        cleaned_data = {}
        
        for _, row in df.iterrows():
            course_id = str(row['Course code']).strip()  # Changed from 'Course Code' to 'Course code'
            cleaned_data[course_id] = {
                'title': str(row['Title']).strip(),
                'length': str(row['Length']).strip(),
                'priority': str(row['Priority']).strip(),
                'available_blocks': str(row['Available blocks']).strip(),
                'unavailable_blocks': str(row['Unavailable blocks']).strip(),
                'min_size': str(row['Minimum section size']).strip(),
                'target_size': str(row['Target section size']).strip(),
                'max_size': str(row['Maximum section size']).strip(),
                'num_sections': str(row['Number of sections']).strip(),
                'total_credits': str(row['Total credits']).strip()
            }
        return cleaned_data

    def clean_student_requests(self, df: pd.DataFrame) -> List:
        """Clean and structure student course requests"""
        cleaned_data = []
        
        for _, row in df.iterrows():
            request_data = {
                'college_year': str(row['College Year']).strip(),
                'start_term': str(row['Request start term']).strip(),
                'title': str(row['Title']).strip(),
                'type': str(row['Type']).strip(),
                'student_id': str(row['student ID']).strip(),
                'course_id': str(row['Course ID']).strip(),
                'length': str(row['Length']).strip(),
                'course_code': str(row['Course code']).strip(),
                'priority': str(row['Priority']).strip(),
                'departments': str(row['Department(s)']).strip(),
                'credits': str(row['Credits']).strip()
            }
            cleaned_data.append(request_data)
        return cleaned_data

    def validate_data(self) -> List[str]:
        """Run validations on the cleaned data"""
        validation_results = []
        
        # Validate course sections
        for course_id, course in self.courses.items():
            try:
                min_size = int(course['min_size'])
                max_size = int(course['max_size'])
                if min_size > max_size:
                    validation_results.append(
                        f"Course {course_id}: Minimum section size ({min_size}) greater than maximum ({max_size})"
                    )
            except (ValueError, KeyError) as e:
                validation_results.append(f"Course {course_id}: Invalid section size values - {str(e)}")
        
        # Validate course lengths
        for course_id, course in self.courses.items():
            try:
                length = int(course['length'])
                if length <= 0:
                    validation_results.append(
                        f"Course {course_id}: Invalid length value ({length})"
                    )
            except (ValueError, KeyError) as e:
                validation_results.append(
                    f"Course {course_id}: Missing or invalid length - {str(e)}"
                )
        
        # Validate room assignments
        for room_id, room in self.rooms.items():
            if not room['course_code']:
                validation_results.append(f"Room {room_id}: No course assigned")
        
        return validation_results

    def generate_insights(self) -> List[str]:
        """Generate insights from the cleaned data"""
        insights = []
        
        # Basic statistics
        insights.append(f"Total number of lecturers: {len(self.lecturers)}")
        insights.append(f"Total number of rooms: {len(self.rooms)}")
        insights.append(f"Total number of courses: {len(self.courses)}")
        insights.append(f"Total number of student requests: {len(self.student_requests)}")
        
        # Course popularity
        course_counts = {}
        for request in self.student_requests:
            course_code = request['course_code']
            if course_code:
                course_counts[course_code] = course_counts.get(course_code, 0) + 1
        
        if course_counts:
            most_popular = max(course_counts.items(), key=lambda x: x[1])
            insights.append(f"Most requested course: {most_popular[0]} with {most_popular[1]} requests")
        
        # Course lengths
        course_lengths = {}
        for course in self.courses.values():
            length = course['length']
            if length:
                course_lengths[length] = course_lengths.get(length, 0) + 1
        
        insights.append("Course length distribution:")
        for length, count in course_lengths.items():
            insights.append(f"- {length}: {count} courses")
        
        return insights

    def save_to_json(self, filename: str):
        """Save all cleaned data to JSON file"""
        output_data = {
            'lecturers': self.lecturers,
            'rooms': self.rooms,
            'courses': self.courses,
            'student_requests': self.student_requests
        }
        
        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2)

    def analyze_room_utilization(self) -> Dict:
        """Analyze room utilization patterns"""
        utilization = {}
        for room_id, room in self.rooms.items():
            suitable_courses = 0
            total_hours = 0
            for course_id, course in self.courses.items():
                suitable_courses += 1
                try:
                    total_hours += float(course['length']) if course['length'].strip() else 0
                except ValueError:
                    logging.warning(f"Invalid length value for course {course_id}: {course['length']}")
                    continue
            
            utilization[room_id] = {
                'suitable_courses': suitable_courses,
                'potential_hours': total_hours,
                'utilization_rate': f"{(suitable_courses / len(self.courses)) * 100:.2f}%"
            }
        return utilization

    def analyze_department_distribution(self) -> Dict:
        """Analyze course distribution across departments"""
        departments = {}
        for request in self.student_requests:
            if 'departments' in request and request['departments']:
                depts = request['departments'].split(';')
                for dept in depts:
                    dept = dept.strip()
                    if not dept:
                        continue
                    if dept not in departments:
                        departments[dept] = {
                            'course_count': 0,
                            'courses': []
                        }
                    departments[dept]['course_count'] += 1
                    if request['course_code'] not in departments[dept]['courses']:
                        departments[dept]['courses'].append(request['course_code'])
        return departments

    def analyze_student_years(self) -> Dict:
        """Analyze student distribution by year"""
        year_distribution = {}
        for request in self.student_requests:
            year = request.get('college_year', 'Unknown')
            if year not in year_distribution:
                year_distribution[year] = {
                    'count': 0,
                    'course_requests': {}
                }
            year_distribution[year]['count'] += 1
            course_code = request.get('course_code', '')
            if course_code:
                year_distribution[year]['course_requests'][course_code] = \
                    year_distribution[year]['course_requests'].get(course_code, 0) + 1
        return year_distribution

    def analyze_potential_conflicts(self) -> List[Dict]:
        """Analyze potential scheduling conflicts"""
        conflicts = []
        
        # Check for course time conflicts
        for request in self.student_requests:
            student_id = request.get('student_id', '')
            course_code = request.get('course_code', '')
            if not student_id or not course_code:
                continue
            
            # Group requests by student
            student_courses = [r['course_code'] for r in self.student_requests 
                             if r['student_id'] == student_id]
            
            # Check for duplicate course requests
            if len(student_courses) != len(set(student_courses)):
                conflicts.append({
                    'type': 'duplicate_request',
                    'student': student_id,
                    'courses': student_courses
                })
        
        return conflicts 
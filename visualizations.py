import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def create_visualizations(processor):
    # Course popularity visualization
    plt.figure(figsize=(12, 6))
    course_requests = {}
    for request in processor.student_requests:
        course_code = request.get('course_code', '')
        if course_code:
            course_requests[course_code] = course_requests.get(course_code, 0) + 1
    
    if course_requests:
        # Sort by popularity and take top 20
        sorted_courses = sorted(course_requests.items(), key=lambda x: x[1], reverse=True)[:20]
        courses, counts = zip(*sorted_courses)
        
        plt.bar(courses, counts)
        plt.title('Top 20 Course Request Distribution')
        plt.xlabel('Course Code')
        plt.ylabel('Number of Requests')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('course_popularity.png')
    
    # Room utilization visualization
    plt.figure(figsize=(10, 6))
    room_util = processor.analyze_room_utilization()
    rooms = list(room_util.keys())
    util_rates = [float(room_util[r]['utilization_rate'].strip('%')) for r in rooms]
    
    plt.bar(rooms, util_rates)
    plt.title('Room Utilization Rates')
    plt.xlabel('Room ID')
    plt.ylabel('Utilization Rate (%)')
    plt.tight_layout()
    plt.savefig('room_utilization.png')
    
    # Student year distribution
    plt.figure(figsize=(8, 8))
    year_counts = {}
    for request in processor.student_requests:
        year = request.get('college_year', 'Unknown')
        if year:
            year_counts[year] = year_counts.get(year, 0) + 1
    
    if year_counts:
        years = list(year_counts.keys())
        counts = [year_counts[y] for y in years]
        
        plt.pie(counts, labels=years, autopct='%1.1f%%')
        plt.title('Student Distribution by Year')
        plt.tight_layout()
        plt.savefig('student_years.png')
    
    # Department distribution
    plt.figure(figsize=(12, 6))
    dept_counts = {}
    for request in processor.student_requests:
        depts = request.get('departments', '').split(';')
        for dept in depts:
            dept = dept.strip()
            if dept:
                dept_counts[dept] = dept_counts.get(dept, 0) + 1
    
    if dept_counts:
        # Sort by count and take top 15 departments
        sorted_depts = sorted(dept_counts.items(), key=lambda x: x[1], reverse=True)[:15]
        depts, counts = zip(*sorted_depts)
        
        plt.figure(figsize=(15, 6))
        plt.bar(depts, counts)
        plt.title('Top 15 Departments by Course Requests')
        plt.xlabel('Department')
        plt.ylabel('Number of Requests')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('department_distribution.png') 
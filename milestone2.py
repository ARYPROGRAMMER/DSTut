from data_processor import DataProcessor
from scheduler import CourseScheduler
import pandas as pd
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_milestone2():
    try:
        processor = DataProcessor()
        excel_file = 'dataset.xlsx'
        
        print("\nReading Excel file...")
        sheets = pd.read_excel(excel_file, sheet_name=None)
        
        # Process each sheet
        print("\nProcessing sheets...")
        processor.lecturers = processor.clean_lecturer_data(sheets['Lecturer Details'])
        processor.rooms = processor.clean_room_data(sheets['Rooms data'])
        processor.courses = processor.clean_course_data(sheets['Course list'])
        processor.student_requests = processor.clean_student_requests(sheets['Student requests'])
        
        print(f"\nProcessed data summary:")
        print(f"Lecturers: {len(processor.lecturers)}")
        print(f"Rooms: {len(processor.rooms)}")
        print(f"Courses: {len(processor.courses)}")
        print(f"Student requests: {len(processor.student_requests)}")
        
        # Create and solve schedule
        print("\nCreating schedule...")
        scheduler = CourseScheduler(processor)
        
        print("Solving scheduling problem...")
        if scheduler.solve():
            print("Successfully created schedule!")
            schedules = scheduler.generate_schedules()
            
            # Save results
            with open('schedules.json', 'w') as f:
                json.dump(schedules, f, indent=2)
            
            # Print statistics
            stats = schedules['stats']
            print("\nScheduling Statistics:")
            print(f"Total Requests: {stats['total_requests']}")
            print(f"Fulfilled Requests: {stats['fulfilled_requests']}")
            print(f"Fulfillment Rate: {(stats['fulfilled_requests']/stats['total_requests'])*100:.2f}%")
            
            print("\nPriority-wise Statistics:")
            for priority, data in stats['priority_stats'].items():
                if data['total'] > 0:
                    fulfill_rate = (data['fulfilled']/data['total'])*100
                    print(f"{priority}: {fulfill_rate:.2f}% fulfilled ({data['fulfilled']}/{data['total']})")
        else:
            print("Could not find a feasible schedule. Try relaxing constraints.")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

def print_schedule_results(schedules):
    print("\nDetailed Schedule Results:")
    print("==========================")
    
    stats = schedules['stats']
    print(f"\nOverall Statistics:")
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Fulfilled Requests: {stats['fulfilled_requests']}")
    print(f"Overall Fulfillment Rate: {(stats['fulfilled_requests']/stats['total_requests'])*100:.2f}%")
    
    print("\nPriority-wise Statistics:")
    for priority, data in stats['priority_stats'].items():
        if data['total'] > 0:
            rate = (data['fulfilled']/data['total'])*100
            print(f"{priority}: {rate:.2f}% fulfilled ({data['fulfilled']}/{data['total']})")
    
    print("\nSample Student Schedule:")
    sample_student = next(iter(schedules['student']))
    print(f"\nStudent {sample_student}:")
    for assignment in schedules['student'][sample_student]:
        print(f"  Course: {assignment['course']}")
        print(f"  Section: {assignment['section']}")
        print(f"  Block: {assignment['block']}")
        print(f"  Room: {assignment['room']}")
        print(f"  Teacher: {assignment['teacher']}")
        print()

if __name__ == "__main__":
    run_milestone2() 
import pandas as pd
from data_processor import DataProcessor
from visualizations import create_visualizations
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # Initialize the data processor
        processor = DataProcessor()
        
        # Read Excel file
        excel_file = 'dataset.xlsx'
        logger.info(f"Reading {excel_file}...")
        
        try:
            # Read all sheets
            all_sheets = pd.read_excel(excel_file, sheet_name=None)
            logger.info(f"Available sheets: {list(all_sheets.keys())}")
            
            # Process each sheet
            for sheet_name, df in all_sheets.items():
                if sheet_name == 'RULES':
                    continue  # Skip rules sheet for now
                
                logger.info(f"Processing {sheet_name}...")
                print(f"\nColumns in {sheet_name}:")
                print(df.columns.tolist())
                print("\nFirst few rows:")
                print(df.head())
                
                # Process based on sheet name
                if sheet_name == 'Lecturer Details':
                    processor.lecturers = processor.clean_lecturer_data(df)
                elif sheet_name == 'Rooms data':
                    processor.rooms = processor.clean_room_data(df)
                elif sheet_name == 'Course list':
                    processor.courses = processor.clean_course_data(df)
                elif sheet_name == 'Student requests':
                    processor.student_requests = processor.clean_student_requests(df)
            
            # Generate insights
            insights = processor.generate_insights()
            print("\nInsights:")
            for insight in insights:
                print(f"- {insight}")
            
            # Create visualizations
            create_visualizations(processor)
            
            # Save processed data
            processor.save_to_json('cleaned_data.json')
            logger.info("Data processing completed successfully!")
            
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            raise
            
    except FileNotFoundError:
        logger.error(f"Could not find {excel_file}")
        print(f"\nError: {excel_file} not found in current directory")
        
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main() 
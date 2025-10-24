import requests
import logging
import argparse
import json
import sys
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("tutorial_marks_test")

def test_tutorial_marks_integration(base_url, student_roll_no, course_id, tutorial_number, marks):
    """
    Test the integration with Academic Analyzer API for updating tutorial marks.
    """
    logger.info(f"Testing tutorial marks integration with {base_url}")
    logger.info(f"Parameters: student={student_roll_no}, course={course_id}, tutorial={tutorial_number}, marks={marks}")
    
    # Format the request
    request_data = {
        "rollno": student_roll_no,
        "courseId": course_id,
        "tutorialNumber": int(tutorial_number),
        "marks": float(marks)
    }
    
    logger.info(f"Request payload: {json.dumps(request_data, indent=2)}")
    
    try:
        # Send the request
        response = requests.post(
            f"{base_url}/student/tutorial-marks",
            json=request_data,
            timeout=10
        )
        
        logger.info(f"Response status code: {response.status_code}")
        
        try:
            response_data = response.json()
            logger.info(f"Response body: {json.dumps(response_data, indent=2)}")
            
            if response.ok and response_data.get('success'):
                logger.info("✅ SUCCESS: Tutorial marks updated successfully")
                return True
            else:
                logger.error(f"❌ ERROR: API returned failure - {response_data.get('message', 'Unknown error')}")
                return False
        except ValueError:
            logger.error(f"❌ ERROR: Invalid JSON response - {response.text[:100]}")
            return False
    except requests.RequestException as e:
        logger.error(f"❌ ERROR: Request failed - {str(e)}")
        return False

def test_get_marks(base_url, student_roll_no, course_id):
    """
    Test getting student marks from the Academic Analyzer API.
    """
    logger.info(f"Testing retrieving marks from {base_url}")
    logger.info(f"Parameters: student={student_roll_no}, course={course_id}")
    
    try:
        # Send the request
        response = requests.get(
            f"{base_url}/student/course-marks",
            params={"rollno": student_roll_no, "courseId": course_id},
            timeout=10
        )
        
        logger.info(f"Response status code: {response.status_code}")
        
        try:
            response_data = response.json()
            if response.ok and response_data.get('success'):
                logger.info("✅ SUCCESS: Retrieved student marks successfully")
                
                # Print tutorial marks
                marks = response_data.get('marks', {})
                tutorial_marks = {
                    k: v for k, v in marks.items() 
                    if k.startswith('tutorial') and k not in ('tutorialAvg', 'tutorialTotal')
                }
                
                logger.info("Tutorial marks:")
                for tut, mark in tutorial_marks.items():
                    logger.info(f"  {tut}: {mark}")
                    
                return True
            else:
                logger.error(f"❌ ERROR: API returned failure - {response_data.get('message', 'Unknown error')}")
                return False
        except ValueError:
            logger.error(f"❌ ERROR: Invalid JSON response - {response.text[:100]}")
            return False
    except requests.RequestException as e:
        logger.error(f"❌ ERROR: Request failed - {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test integration with Academic Analyzer API")
    parser.add_argument("--url", default="http://localhost:5000", help="Base URL for Academic Analyzer API")
    parser.add_argument("--student", required=True, help="Student roll number")
    parser.add_argument("--course", required=True, help="Course ID")
    parser.add_argument("--tutorial", type=int, choices=[1, 2, 3, 4], help="Tutorial number (1-4)")
    parser.add_argument("--marks", type=float, help="Marks to update (0-100)")
    parser.add_argument("--get", action="store_true", help="Get current marks instead of updating")
    
    args = parser.parse_args()
    
    if args.get:
        # Get current marks
        success = test_get_marks(args.url, args.student, args.course)
    else:
        # Update marks
        if args.tutorial is None or args.marks is None:
            parser.error("--tutorial and --marks are required when updating marks")
        
        success = test_tutorial_marks_integration(
            args.url, args.student, args.course, args.tutorial, args.marks
        )
    
    sys.exit(0 if success else 1)
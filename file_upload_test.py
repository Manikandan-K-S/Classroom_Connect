#!/usr/bin/env python
"""
File Upload and Question Generation Test for Classroom Connect

This script helps diagnose issues with uploading files and generating questions.
It simulates a file upload to the generate_questions_from_content endpoint and
displays the API response.
"""

import os
import sys
import json
import base64
import argparse
import requests  # Global import of requests
from datetime import datetime

def load_file(file_path):
    """Load file and encode it as base64."""
    try:
        # Make sure path is properly stripped of whitespace and quotes
        file_path = file_path.strip().strip('"\'')
        
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            encoded = base64.b64encode(file_bytes).decode("utf-8")
            return f"data:{get_mime_type(file_path)};base64,{encoded}"
    except Exception as e:
        print(f"Error loading file: {e}")
        sys.exit(1)

def get_mime_type(file_path):
    """Determine MIME type from file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    mime_types = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".doc": "application/msword",
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".html": "text/html",
        ".htm": "text/html"
    }
    return mime_types.get(ext, "application/octet-stream")

def get_file_info(file_path):
    """Get file information."""
    try:
        # Trim any leading/trailing whitespace and quotes from the path
        file_path = file_path.strip().strip('"\'')
        
        if not os.path.exists(file_path):
            print(f"ERROR: File not found: {file_path}")
            return {
                "path": file_path,
                "name": "File not found",
                "error": "File does not exist"
            }
            
        size_bytes = os.path.getsize(file_path)
        size_kb = size_bytes / 1024
        size_mb = size_kb / 1024
        
        if size_mb >= 1:
            size_str = f"{size_mb:.2f} MB"
        else:
            size_str = f"{size_kb:.2f} KB"
            
        return {
            "path": file_path,
            "name": os.path.basename(file_path),
            "size_bytes": size_bytes,
            "size_str": size_str,
            "mime_type": get_mime_type(file_path),
            "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"Error getting file info: {e}")
        return {"path": file_path, "name": "Unknown file", "error": str(e)}

def get_csrf_and_session(url):
    """Attempt to get a CSRF token and session cookie from the server."""
    try:
        import requests
        
        # Get the base URL (without the endpoint part)
        base_url = "/".join(url.split("/")[:3])  # Just get scheme and domain
        if not base_url.endswith("/"):
            base_url += "/"
            
        # Add auth endpoints
        login_url = f"{base_url}staff/login/"
        
        print(f"Attempting to authenticate with: {login_url}")
        
        # First request to get CSRF cookie
        session = requests.Session()
        
        # Get the login page to get the CSRF token
        response = session.get(login_url)
        if response.status_code != 200:
            print(f"Failed to access login page: {response.status_code}")
            return None
            
        # Get CSRF token from cookies
        csrf_token = None
        if 'csrftoken' in session.cookies:
            csrf_token = session.cookies['csrftoken']
            print(f"Got CSRF token: {csrf_token[:5]}...")
        else:
            print("No CSRF token found in cookies")
            
        # Format cookies for use with the script
        cookies_str = "; ".join([f"{k}={v}" for k, v in session.cookies.items()])
        
        # Add a more detailed diagnostic message
        cookie_info = "\n".join([f"  {k}: {v}" for k, v in session.cookies.items()])
        print(f"Current cookies:\n{cookie_info}")
        
        # Return the information
        return {
            "csrf_token": csrf_token,
            "cookies": cookies_str,
            "session": session,
            "login_url": login_url
        }
    except Exception as e:
        print(f"Error getting CSRF token: {e}")
        return None

def test_upload(file_path, url, num_questions=3, difficulty="medium", 
                question_types=None, cookie=None, csrf_token=None, login_credentials=None):
    """Test uploading a file and generating questions."""
    # Import requests here to make sure we have access to it
    import requests
    
    if question_types is None:
        question_types = ["mcq_single", "mcq_multiple", "true_false"]
        
    file_info = get_file_info(file_path)
    
    print("=" * 60)
    print(f"FILE UPLOAD TEST: {file_info['name']}")
    print("=" * 60)
    print(f"File: {file_info['path']}")
    print(f"Size: {file_info['size_str']}")
    print(f"Type: {file_info['mime_type']}")
    print(f"Modified: {file_info['modified']}")
    print(f"API URL: {url}")
    
    # Check if file is too large
    if file_info['size_bytes'] > 10 * 1024 * 1024:  # 10 MB limit
        print("\nWARNING: File is larger than 10MB, which may be too large for API processing.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != "y":
            print("Aborted.")
            sys.exit(0)
    
    # Load and encode file
    print("\nEncoding file as base64...")
    encoded_file = load_file(file_path)
    
    # Prepare request payload
    payload = {
        "fileContent": encoded_file,
        "fileType": file_info['mime_type'],
        "numQuestions": num_questions,
        "difficulty": difficulty,
        "questionTypes": question_types
    }
    
    # Set up headers and cookies
    headers = {"Content-Type": "application/json"}
    cookies = {}
    
    # Handle session cookie
    if cookie:
        try:
            # Handle multiple cookies (sessionid and csrftoken)
            if ";" in cookie:
                cookie_parts = cookie.split(";")
                for part in cookie_parts:
                    if "=" in part:
                        key, value = part.strip().split("=", 1)
                        cookies[key] = value
                        print(f"Using cookie: {key}=***")
            # Handle single cookie
            elif "=" in cookie:
                key, value = cookie.split("=", 1)
                cookies[key] = value
                print(f"Using cookie: {key}=***")
            else:
                print(f"Warning: Invalid cookie format. Expected 'key=value', got '{cookie}'")
        except Exception as e:
            print(f"Warning: Error parsing cookie: {e}")
    
    # Handle CSRF token
    if csrf_token:
        headers["X-CSRFToken"] = csrf_token
        print(f"Using CSRF token: {csrf_token[:5]}***")
        
    # Get CSRF from cookies if present
    if "csrftoken" in cookies and not csrf_token:
        headers["X-CSRFToken"] = cookies["csrftoken"]
        print(f"Using CSRF token from cookie: {cookies['csrftoken'][:5]}***")
        
    # If login credentials are provided, try to log in first
    if login_credentials:
        print("\nAttempting to login as staff...")
        
        # Get the base URL to find the login page
        base_url = "/".join(url.split("/")[:3])  # Just get scheme and domain
        if not base_url.endswith("/"):
            base_url += "/"
        
        # Try several possible login URLs
        login_urls = [
            f"{base_url}academic_integration/staff/login/",  # This is the correct URL based on the project structure
            f"{base_url}staff/login/",
            f"{base_url}quiz/staff/login/",
            f"{base_url}accounts/login/",
            f"{base_url}login/"
        ]
        
        login_success = False
        session = requests.Session()
        
        for login_url in login_urls:
            print(f"Trying login URL: {login_url}")
            
            # First get the login page to get the CSRF token
            try:
                login_page = session.get(login_url)
                print(f"Login page status: {login_page.status_code}")
                
                if login_page.status_code != 200:
                    print(f"Skipping URL {login_url} (status code: {login_page.status_code})")
                    continue
                    
                # Check for CSRF token
                if 'csrftoken' in session.cookies:
                    csrf_for_login = session.cookies['csrftoken']
                    print(f"Got login CSRF token: {csrf_for_login[:5]}***")
                    
                    # Now login with the credentials
                    email, password = login_credentials
                    
                    # Try different form field names for Django login
                    login_attempts = [
                        {"email": email, "password": password, "csrfmiddlewaretoken": csrf_for_login},
                        {"username": email, "password": password, "csrfmiddlewaretoken": csrf_for_login}
                    ]
                    
                    for login_data in login_attempts:
                        login_headers = {
                            "Referer": login_url,
                            "X-CSRFToken": csrf_for_login
                        }
                        
                        print(f"Attempting login with fields: {', '.join(login_data.keys())}")
                        login_response = session.post(login_url, data=login_data, headers=login_headers)
                        
                        if login_response.status_code == 200 or login_response.status_code == 302:
                            print("Login successful!")
                            
                            # Update cookies and CSRF token with the authenticated session
                            cookies = session.cookies.get_dict()
                            print(f"Authenticated cookies: {', '.join(cookies.keys())}")
                            
                            if 'csrftoken' in cookies:
                                csrf_token = cookies['csrftoken']
                                headers["X-CSRFToken"] = csrf_token
                                print(f"Using authenticated CSRF token: {csrf_token[:5]}***")
                                
                            login_success = True
                            break
                        else:
                            print(f"Login attempt failed with status code: {login_response.status_code}")
                    
                    if login_success:
                        break
                else:
                    print("No CSRF token found on login page")
            except Exception as e:
                print(f"Error trying login URL {login_url}: {e}")
        
        if not login_success:
            print("All login attempts failed. Will continue without authentication.")
    
    # Make API request
    print("\nSending request to API...")
    try:
        # Print detailed request information for debugging
        print("\nRequest details:")
        print(f"URL: {url}")
        print(f"Headers: {json.dumps({k: v[:10] + '...' if k.lower() == 'x-csrftoken' and len(v) > 10 else v for k, v in headers.items()})}")
        print(f"Cookies: {json.dumps({k: v[:5] + '...' if len(v) > 5 else v for k, v in cookies.items()})}")
        print(f"Payload: {json.dumps({k: '(data omitted)' if k == 'fileContent' else v for k, v in payload.items()})}")
        
        response = requests.post(
            url, 
            json=payload, 
            headers=headers,
            cookies=cookies,
            timeout=60  # Longer timeout for API processing
        )
        
        print(f"\nAPI Response Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("\nAPI Response Content:")
                print(json.dumps(result, indent=2))
                
                if result.get("success"):
                    questions = result.get("questions", [])
                    print(f"\n✓ Success! Generated {len(questions)} questions.")
                    
                    # Print sample of first question
                    if questions:
                        print("\nSample Question:")
                        print(f"Question: {questions[0]['text']}")
                        if questions[0].get("choices"):
                            print("Choices:")
                            for i, choice in enumerate(questions[0]["choices"]):
                                correct = "✓" if choice.get("is_correct") else " "
                                print(f"  {i+1}. [{correct}] {choice['text']}")
                else:
                    print(f"\n✗ API Error: {result.get('error', 'Unknown error')}")
                    
            except json.JSONDecodeError:
                print("\n✗ Failed to parse JSON response:")
                print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
        else:
            print("\n✗ API request failed:")
            print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
            
            # If it's a 403, provide more specific guidance
            if response.status_code == 403:
                print("\nAuthorization Error: The API requires staff login.")
                print("Try running the script with staff credentials:")
                print("python file_upload_test.py \"path/to/file.pdf\" --staff-email \"admin@example.com\" --staff-password \"your_password\"")
            
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Request failed: {str(e)}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test file upload and question generation")
    parser.add_argument("file", help="Path to the file to upload")
    parser.add_argument("--url", default="http://localhost:8000/academic_integration/api/generate-questions/", 
                        help="API endpoint URL (default: http://localhost:8000/academic_integration/api/generate-questions/)")
    parser.add_argument("--questions", type=int, default=3, help="Number of questions to generate (default: 3)")
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard"], default="medium",
                        help="Question difficulty (default: medium)")
    parser.add_argument("--types", nargs="+", choices=["mcq_single", "mcq_multiple", "true_false", "text"], 
                        default=["mcq_single", "mcq_multiple", "true_false"],
                        help="Question types to generate (default: mcq_single mcq_multiple true_false)")
    parser.add_argument("--cookie", help="Session cookie(s) in format 'key=value' or 'key1=value1;key2=value2'")
    parser.add_argument("--csrf", help="CSRF token for Django authentication")
    parser.add_argument("--auth", action="store_true", help="Get session and CSRF tokens automatically")
    parser.add_argument("--staff-email", help="Staff email for login (use with --staff-password)")
    parser.add_argument("--staff-password", help="Staff password for login (use with --staff-email)")
    parser.add_argument("--debug", action="store_true", help="Show detailed debug information")
    
    args = parser.parse_args()
    
    cookie = args.cookie
    csrf_token = args.csrf
    login_credentials = None
    
    # Enable debug mode if requested
    if args.debug:
        import logging
        import http.client as http_client
        http_client.HTTPConnection.debuglevel = 1
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
        print("Debug mode enabled. Showing detailed request information.")
    
    # Check if login credentials are provided
    if args.staff_email and args.staff_password:
        login_credentials = (args.staff_email, args.staff_password)
        print(f"Staff login credentials provided for: {args.staff_email}")
    
    # Try to get authentication tokens automatically if requested
    if args.auth:
        auth_info = get_csrf_and_session(args.url)
        if auth_info:
            if not cookie:
                cookie = auth_info["cookies"]
            if not csrf_token:
                csrf_token = auth_info["csrf_token"]
    
    test_upload(
        file_path=args.file.strip(),  # Just strip spaces, quotes are handled in get_file_info
        url=args.url,
        num_questions=args.questions,
        difficulty=args.difficulty,
        question_types=args.types,
        cookie=cookie,
        csrf_token=csrf_token,
        login_credentials=login_credentials
    )
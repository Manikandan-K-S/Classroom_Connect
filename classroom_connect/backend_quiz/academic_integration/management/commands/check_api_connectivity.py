from django.core.management.base import BaseCommand
import logging
import requests
import time
from django.conf import settings

class Command(BaseCommand):
    help = 'Check Academic Analyzer API connectivity and diagnose any issues'
    
    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true', help='Show detailed logging')
        parser.add_argument('--endpoints', nargs='*', help='Check specific endpoints only')
    
    def handle(self, *args, **options):
        verbose = options['verbose']
        specific_endpoints = options.get('endpoints')
        
        if verbose:
            self.stdout.write(self.style.SUCCESS('Running detailed API connectivity check...'))
        else:
            self.stdout.write(self.style.SUCCESS('Running API connectivity check...'))
        
        # Get base URL for Academic Analyzer API
        try:
            base_url = getattr(settings, "ACADEMIC_ANALYZER_BASE_URL", "http://localhost:5000").rstrip("/")
            self.stdout.write(f"Using API base URL: {base_url}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error getting Academic Analyzer API URL: {e}"))
            return
        
        # Define endpoints to check
        endpoints = [
            {
                'name': 'health',
                'method': 'GET',
                'path': '/health',
                'params': {},
                'body': None
            },
            {
                'name': 'student auth',
                'method': 'POST',
                'path': '/student/auth',
                'params': {},
                'body': {'rollno': 'test_student', 'password': 'test_password'}
            },
            {
                'name': 'staff auth',
                'method': 'POST',
                'path': '/staff/auth',
                'params': {},
                'body': {'email': 'test_staff@example.com', 'password': 'test_password'}
            },
            {
                'name': 'student dashboard',
                'method': 'GET',
                'path': '/student/dashboard',
                'params': {'rollno': 'test_student'},
                'body': None
            },
            {
                'name': 'tutorial marks',
                'method': 'POST',
                'path': '/student/tutorial-marks',
                'params': {},
                'body': {
                    'rollno': 'test_student',
                    'courseId': 'TEST101',
                    'tutorialNumber': 1,
                    'marks': 80.0
                }
            }
        ]
        
        # Filter endpoints if specified
        if specific_endpoints:
            endpoints = [e for e in endpoints if e['name'] in specific_endpoints]
            self.stdout.write(f"Checking only endpoints: {', '.join([e['name'] for e in endpoints])}")
        
        overall_success = True
        results = []
        
        for endpoint in endpoints:
            start_time = time.time()
            success = False
            message = ""
            response_status = None
            response_body = None
            
            try:
                if verbose:
                    self.stdout.write(f"Testing {endpoint['method']} {endpoint['path']}...")
                
                if endpoint['method'] == 'GET':
                    response = requests.get(
                        f"{base_url}{endpoint['path']}",
                        params=endpoint['params'],
                        timeout=5
                    )
                elif endpoint['method'] == 'POST':
                    response = requests.post(
                        f"{base_url}{endpoint['path']}",
                        params=endpoint['params'],
                        json=endpoint['body'],
                        timeout=5
                    )
                else:
                    raise ValueError(f"Unsupported method: {endpoint['method']}")
                
                response_status = response.status_code
                try:
                    response_body = response.json()
                except ValueError:
                    response_body = {"text": response.text[:100] + "..." if len(response.text) > 100 else response.text}
                
                # We consider 404/403/401 as the API being available but the credentials being incorrect
                if response.ok or response_status in [401, 403, 404]:
                    success = True
                    message = f"API responded with status {response_status}"
                    if verbose and response_body:
                        if isinstance(response_body, dict):
                            message += f", success: {response_body.get('success', 'N/A')}"
                            if 'message' in response_body:
                                message += f", message: {response_body['message']}"
                else:
                    success = False
                    message = f"API responded with error status {response_status}"
                    overall_success = False
                
            except requests.RequestException as e:
                success = False
                message = f"Request error: {e}"
                overall_success = False
            
            elapsed_time = time.time() - start_time
            
            # Log result
            if success:
                self.stdout.write(self.style.SUCCESS(
                    f"✓ {endpoint['name']}: {message} ({elapsed_time:.2f}s)"
                ))
            else:
                self.stdout.write(self.style.ERROR(
                    f"✗ {endpoint['name']}: {message} ({elapsed_time:.2f}s)"
                ))
            
            # Store result
            results.append({
                'endpoint': endpoint['name'],
                'method': endpoint['method'],
                'path': endpoint['path'],
                'success': success,
                'status': response_status,
                'message': message,
                'elapsed_time': elapsed_time,
                'response': response_body if verbose else None
            })
        
        # Print summary
        self.stdout.write("\nSummary:")
        self.stdout.write("--------")
        success_count = sum(1 for r in results if r['success'])
        self.stdout.write(f"Endpoints checked: {len(results)}")
        self.stdout.write(f"Successful: {success_count}")
        self.stdout.write(f"Failed: {len(results) - success_count}")
        
        if overall_success:
            self.stdout.write(self.style.SUCCESS("\nAcademic Analyzer API appears to be working correctly."))
        else:
            self.stdout.write(self.style.ERROR(
                "\nOne or more endpoints failed. Please check the API server or configuration."
            ))
        
        # Print detailed results in verbose mode
        if verbose:
            self.stdout.write("\nDetailed Results:")
            self.stdout.write("-----------------")
            for result in results:
                self.stdout.write(f"\n{result['method']} {result['path']} ({result['endpoint']})")
                self.stdout.write(f"Success: {result['success']}")
                self.stdout.write(f"Status: {result['status']}")
                self.stdout.write(f"Message: {result['message']}")
                self.stdout.write(f"Time: {result['elapsed_time']:.2f}s")
                if result['response']:
                    self.stdout.write(f"Response: {result['response']}")
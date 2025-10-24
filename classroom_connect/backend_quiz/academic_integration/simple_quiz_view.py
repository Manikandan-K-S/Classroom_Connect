from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
import requests
import logging
import os

# Import common utilities
from .views import _api_base_url, _safe_json

# Set up logging
logger = logging.getLogger(__name__)

def simple_quiz_generation(request: HttpRequest) -> HttpResponse:
    """
    View for staff to use the simplified quiz generation interface with direct Gemini integration.
    This page allows staff to upload a file and quickly generate a quiz without complex options.
    """
    # Ensure staff is logged in
    staff_email = request.session.get('staff_email')
    if not staff_email:
        messages.info(request, "Please log in to continue.")
        return redirect("academic_integration:staff_login")
    
    # Get courses for the dropdown menu
    courses = []
    try:
        response = requests.get(
            f"{_api_base_url()}/staff/dashboard",
            params={"email": staff_email},
            timeout=5,
        )
        if response.ok:
            data = _safe_json(response)
            if data.get('success'):
                courses = data.get('courses', [])
    except requests.RequestException:
        logger.exception("Failed to fetch courses for simple quiz generation page")
    
    # Check if Gemini API key is available
    api_key_available = bool(os.environ.get("GEMINI_API_KEY"))
    if not api_key_available:
        messages.warning(request, "Gemini API key is not configured. Quiz generation may not work properly.")
        logger.warning("GEMINI_API_KEY environment variable is not set when accessing the quiz generation page")
    
    context = {
        'staff_email': staff_email,
        'staff_name': request.session.get('staff_name', staff_email),
        'courses': courses,
        'api_key_available': api_key_available
    }
    return render(request, "academic_integration/simple_quiz_generation.html", context)
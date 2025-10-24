from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from quiz.models import Quiz

def is_staff(user):
    """Check if the user is a staff member."""
    return user.is_authenticated and hasattr(user, 'staff')

@user_passes_test(is_staff)
def debug_quiz_availability(request, quiz_id=None):
    """
    Debug view for administrators to check quiz availability status
    and diagnose "Quiz not available" issues.
    """
    context = {
        'now': timezone.now(),
        'server_timezone': timezone.get_current_timezone_name(),
    }
    
    if quiz_id:
        # Specific quiz debugging
        quiz = get_object_or_404(Quiz, id=quiz_id)
        
        # Check if dates are timezone-aware
        start_date_aware = "Timezone-aware" if quiz.start_date and not timezone.is_naive(quiz.start_date) else "Naive (no timezone)"
        complete_by_date_aware = "Timezone-aware" if quiz.complete_by_date and not timezone.is_naive(quiz.complete_by_date) else "Naive (no timezone)"
        
        # Calculate availability
        is_available = quiz.is_available()
        
        # Debug information
        context.update({
            'quiz': quiz,
            'start_date_aware': start_date_aware,
            'complete_by_date_aware': complete_by_date_aware,
            'is_available': is_available,
            'availability_reasons': {
                'start_date_passed': quiz.start_date is None or quiz.start_date <= timezone.now(),
                'not_completed_yet': quiz.complete_by_date is None or quiz.complete_by_date >= timezone.now(),
                'is_active': quiz.is_active,
            }
        })
    else:
        # List all quizzes with availability status
        quizzes = Quiz.objects.all().order_by('-start_date')
        quiz_availability = []
        
        for quiz in quizzes:
            quiz_availability.append({
                'id': quiz.id,
                'title': quiz.title,
                'start_date': quiz.start_date,
                'complete_by_date': quiz.complete_by_date,
                'is_active': quiz.is_active,
                'is_available': quiz.is_available(),
                'start_date_aware': "Timezone-aware" if quiz.start_date and not timezone.is_naive(quiz.start_date) else "Naive (no timezone)",
                'complete_by_date_aware': "Timezone-aware" if quiz.complete_by_date and not timezone.is_naive(quiz.complete_by_date) else "Naive (no timezone)",
            })
        
        context['quiz_availability'] = quiz_availability
    
    return render(request, 'academic_integration/debug_quiz_availability.html', context)

@user_passes_test(is_staff)
def debug_quiz_timezone(request):
    """
    Debug view for checking timezone configuration.
    """
    from django.conf import settings
    
    context = {
        'now': timezone.now(),
        'server_timezone': timezone.get_current_timezone_name(),
        'timezone_settings': {
            'TIME_ZONE': settings.TIME_ZONE,
            'USE_TZ': settings.USE_TZ,
        }
    }
    
    # Check if we can format times properly
    sample_time = timezone.now()
    context['sample_time'] = {
        'value': sample_time,
        'iso_format': sample_time.isoformat(),
        'str_representation': str(sample_time),
    }
    
    if request.GET.get('format') == 'json':
        return JsonResponse(context, json_encoder=timezone.DjangoJSONEncoder)
    
    return render(request, 'academic_integration/debug_quiz_timezone.html', context)
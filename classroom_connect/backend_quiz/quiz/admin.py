from django.contrib import admin
from django.utils.html import format_html
from .models import Quiz, Question, Choice, QuizAttempt, QuizAnswer, User

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2  # show 2 empty choice fields by default


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'quiz_type', 'course_id', 'tutorial_number', 'created_at', 'is_active']
    list_filter = ['quiz_type', 'is_active', 'course_id']
    search_fields = ['title', 'course_id']
    inlines = [QuestionInline]


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'quiz', 'points']
    list_filter = ['quiz']
    search_fields = ['text']
    inlines = [ChoiceInline]


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['text', 'question', 'is_correct']
    list_filter = ['question__quiz', 'is_correct']
    search_fields = ['text']


class QuizAnswerInline(admin.TabularInline):
    model = QuizAnswer
    extra = 0
    readonly_fields = ['question', 'display_selected_choices', 'points_earned']
    can_delete = False
    
    def display_selected_choices(self, obj):
        if obj.selected_choices.exists():
            return ", ".join([choice.text for choice in obj.selected_choices.all()])
        elif obj.text_answer:
            return f"Text: {obj.text_answer}"
        elif obj.boolean_answer is not None:
            return f"{'True' if obj.boolean_answer else 'False'}"
        return "-"
    
    display_selected_choices.short_description = "Selected Choices"


class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'quiz', 'score', 'percentage', 'completed_status', 'sync_status', 'started_at']
    list_filter = ['status', 'marks_synced', 'quiz__quiz_type']
    search_fields = ['user__username', 'quiz__title']
    readonly_fields = ['score', 'percentage', 'started_at', 'completed_at', 'last_sync_at']
    inlines = [QuizAnswerInline]
    
    def completed_status(self, obj):
        if obj.completed_at:
            return format_html('<span style="color:green;">Completed</span>')
        return format_html('<span style="color:orange;">In Progress</span>')
    
    def sync_status(self, obj):
        if not obj.quiz.quiz_type == 'tutorial' or not obj.quiz.course_id:
            return format_html('<span style="color:gray;">N/A</span>')
        
        if obj.completed_at is None:
            return format_html('<span style="color:gray;">Not Completed</span>')
            
        if obj.marks_synced:
            return format_html(
                '<span style="color:green;">Synced</span> at {}'.format(
                    obj.last_sync_at.strftime('%Y-%m-%d %H:%M:%S') if obj.last_sync_at else 'Unknown'
                )
            )
        return format_html('<span style="color:red;">Not Synced</span>')
    
    completed_status.short_description = 'Status'
    sync_status.short_description = 'Sync Status'


class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'display_selected_choices', 'points_earned']
    list_filter = ['attempt__quiz']
    search_fields = ['attempt__user__username', 'question__text']
    
    def display_selected_choices(self, obj):
        if obj.selected_choices.exists():
            return ", ".join([choice.text for choice in obj.selected_choices.all()])
        elif obj.text_answer:
            return f"Text: {obj.text_answer}"
        elif obj.boolean_answer is not None:
            return f"{'True' if obj.boolean_answer else 'False'}"
        return "-"
    
    display_selected_choices.short_description = "Selected Choices"


admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(QuizAttempt, QuizAttemptAdmin)
admin.site.register(QuizAnswer, QuizAnswerAdmin)

from django.db import models
from quiz.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=50, blank=True, null=True)  # Academic analyzer ID
    
    def __str__(self):
        return self.user.username or self.student_id

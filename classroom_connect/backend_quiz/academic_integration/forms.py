from django import forms


class StaffLoginForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "staff@example.com"}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}))


class StudentLoginForm(forms.Form):
    rollno = forms.CharField(label="Roll Number", widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "24MX112"}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}))


class CourseForm(forms.Form):
    course_name = forms.CharField(
        label="Course Name", 
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Database Management Systems"})
    )
    course_code = forms.CharField(
        label="Course Code", 
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. CS101"})
    )
    batch = forms.CharField(
        label="Batch", 
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 24MXG1"})
    )


class StudentForm(forms.Form):
    name = forms.CharField(
        label="Student Name", 
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Full Name"})
    )
    rollno = forms.CharField(
        label="Roll Number", 
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 24MX112"})
    )
    batch = forms.CharField(
        label="Batch", 
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 24MXG1"})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "e.g. student@psgtech.ac.in"})
    )
    password = forms.CharField(
        label="Password", 
        required=False,
        help_text="Leave blank to use roll number as password",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )


class BatchEnrollmentForm(forms.Form):
    batch = forms.CharField(
        label="Batch to Enroll", 
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 24MXG1"})
    )


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="CSV File",
        widget=forms.FileInput(attrs={"class": "form-control", "accept": ".csv"})
    )


class StudentAddForm(forms.Form):
    rollno = forms.CharField(
        label="Student Roll Number", 
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 24MX112"})
    )

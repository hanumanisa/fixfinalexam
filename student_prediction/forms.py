from django import forms
from .models import Instructor, Course, Semester, CourseDifficulty

class InstructorPerformanceForm(forms.Form):
    Instructor = forms.ModelChoiceField(
        queryset=Instructor.objects.all(),
        label="Name of Instructor",
        #to_field_name='instructor_name'
    )
    course_name = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        label="Course Name",
        #to_field_name='course_name'
    )
    avg_grade = forms.FloatField(
        label="Average Grade",
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={'step': '0.1'})
    )
    avg_attendance = forms.FloatField(
        label="Average Attendance",
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={'step': '0.1'})
    )
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.all().distinct(),
        label="Semester",
        #to_field_name='semester_name'
    )
    total_student = forms.IntegerField(
        label="Total Students",
        min_value=1
    )
    difficulty_level = forms.CharField(
        label="Difficulty Level",
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

class CourseRecommendationForm(forms.Form):
    COURSE_DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        label="Course",
        empty_label="-- Choose Course --",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    average_score = forms.FloatField(
        label="Average Score",
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    attendance_percentage = forms.FloatField(
        label="Attendance Percentage",
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    difficulty_level = forms.ChoiceField(
        choices=COURSE_DIFFICULTY_CHOICES,
        label="Difficulty",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.all()
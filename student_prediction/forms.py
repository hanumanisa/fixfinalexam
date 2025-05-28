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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.all().select_related('department')
    
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        label="Select Course",
        empty_label="-- Select Course --"
    )
    
    next_academic_year = forms.CharField(
        label="Next Academic Year",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. 2025/2026'
        })
    )
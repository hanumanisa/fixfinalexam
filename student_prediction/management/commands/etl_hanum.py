from django.core.management.base import BaseCommand
import pandas as pd
from student_prediction.models import Assessment

class Command(BaseCommand):
    help = "ETL: Export assessment data with course, difficulty, student, and department info to CSV"
    
    def handle(self, *args, **kwargs):
        assessments = Assessment.objects.select_related(
            'enrollment__student__department',
            'enrollment__course__coursedifficulty'
        ).all()
        
        data = []
        for a in assessments:
            # pastikan semua data relasi ada
            if (
                a.enrollment and 
                a.enrollment.student and 
                a.enrollment.student.department and 
                a.enrollment.course and 
                hasattr(a.enrollment.course, 'coursedifficulty')
            ):
                data.append({
                    'assessment_id': a.assessment_id,
                    'assessment_type': a.assessment_type,
                    'score': a.score,
                    'enroll_id': a.enrollment.enroll_id,
                    'course_id': a.enrollment.course.course_id,
                    'course_name': a.enrollment.course.course_name,
                    'difficulty_level': a.enrollment.course.coursedifficulty.difficulty_level,
                    'stu_id': a.enrollment.student.stu_id,
                    'student_name': a.enrollment.student.name,
                    'dept_name': a.enrollment.student.department.dept_name
                })
                
        # convert ke dataframe
        df = pd.DataFrame(data)
        
        # export ke csv
        df.to_csv('course_example_new.csv', index=False)
        self.stdout.write(self.style.SUCCESS('Course assessment CSV successfully exported!'))
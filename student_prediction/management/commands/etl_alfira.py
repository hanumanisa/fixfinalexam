from django.core.management.base import BaseCommand
import pandas as pd
from django.db.models import Avg
from student_prediction.models import (
    CourseInstructor, Enrollment, Attendance, CourseDifficulty
)

class Command(BaseCommand):
    help = "ETL: Extract instructor-course-student performance data for all courses with difficulty_level included"

    def handle(self, *args, **options):
        data = []
        course_instructors = CourseInstructor.objects.all().order_by('instructor__instructor_id')

        for ci in course_instructors:
            # Ambil difficulty_level dari CourseDifficulty berdasarkan course_id
            difficulty_obj = CourseDifficulty.objects.filter(course_id=ci.course.course_id).first()
            difficulty_level = difficulty_obj.difficulty_level if difficulty_obj else 'Unknown'

            enrollments = Enrollment.objects.filter(
                course=ci.course,
                semester=ci.semester
            )
            enrollment_ids = enrollments.values_list('enroll_id', flat=True)

            avg_grade = enrollments.aggregate(avg=Avg('grade'))['avg'] or 0
            student_count = enrollments.count()

            avg_attend = Attendance.objects.filter(
                enroll_id__in=enrollment_ids
            ).aggregate(avg=Avg('attendance_percentage'))['avg'] or 0

            data.append({
                'instructor_id': ci.instructor.instructor_id,
                'instructor_name': ci.instructor.instructor_name,
                'course_id': ci.course.course_id,
                'course_name': ci.course.course_name,
                'semester_name': ci.semester.semester_name,
                'difficulty_level': difficulty_level,
                'student_count': student_count,
                'avg_grade': round(avg_grade, 2),
                'avg_attendance': round(avg_attend, 2),
            })

        df = pd.DataFrame(data)
        df.to_csv('all_courses_dataset.csv', index=False)
        self.stdout.write(self.style.SUCCESS('Dataset saved to all_courses_dataset.csv.'))

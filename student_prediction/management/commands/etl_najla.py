from django.core.management.base import BaseCommand
import pandas as pd
from student_prediction.models import Enrollment, Attendance, Assessment
from django.db.models import Avg


class Command(BaseCommand):
    help = "ETL: Extract learn style data and save as CSV"

    def handle(self, *args, **kwargs):
        data = []

        enrollments = Enrollment.objects.all()

        for enrollment in enrollments:
            stu_id = enrollment.student.stu_id  # Ambil dari relasi FK ke Student

            # Hitung rata-rata score assessment untuk enrollment ini
            assessments = Assessment.objects.filter(enrollment=enrollment)
            avg_score = assessments.aggregate(avg_score=Avg('score'))['avg_score'] or 0

            # Ambil kehadiran
            try:
                attendance = Attendance.objects.get(enroll=enrollment)
                attendance_percentage = attendance.attendance_percentage
            except Attendance.DoesNotExist:
                attendance_percentage = 0

            data.append({
                'stu_id': stu_id,
                'attendance_percentage': attendance_percentage,
                'avg_assessment_score': round(avg_score, 2),
            })

        # Simpan ke CSV
        df = pd.DataFrame(data)
        df.to_csv('learnstyle_dataset.csv', index=False)
        self.stdout.write(self.style.SUCCESS('Learn style dataset saved to learnstyle_dataset.csv'))

from django.db import models

class Department(models.Model):
    dept_id = models.IntegerField(primary_key=True)
    dept_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'department'
        managed = False


class Student(models.Model):
    stu_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.DO_NOTHING, db_column='dept_id', null=True, blank=True)

    class Meta:
        db_table = 'student'
        managed = False


class Course(models.Model):
    course_id = models.IntegerField(primary_key=True)
    course_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.DO_NOTHING, db_column='dept_id', null=True, blank=True)

    class Meta:
        db_table = 'course'
        managed = False

    def __str__(self):
        return self.course_name


class CourseDifficulty(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, db_column='course_id', primary_key=True)
    difficulty_level = models.CharField(max_length=50)

    class Meta:
        db_table = 'course_difficulty'
        managed = False


class Enrollment(models.Model):
    enroll_id = models.IntegerField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='course_id', null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_column='stu_id', null=True, blank=True)

    class Meta:
        db_table = 'enrollment'
        managed = False


class Assessment(models.Model):
    assessment_id = models.IntegerField(primary_key=True)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, db_column='enroll_id', null=True, blank=True)
    assessment_type = models.CharField(max_length=50)
    score = models.IntegerField()

    class Meta:
        db_table = 'assessment'
        managed = False


class CourseRecommendation(models.Model):
    course1 = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='recommendation_from')
    course2 = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='recommendation_to')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    support = models.FloatField()
    confidence = models.FloatField()
    lift = models.FloatField()

    class Meta:
        db_table = 'course_recommendation'
        managed = True 
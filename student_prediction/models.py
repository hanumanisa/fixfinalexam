from django.db import models

class Department(models.Model):
    dept_id = models.IntegerField(primary_key=True)
    dept_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'department'
        managed = False


class Student(models.Model):
    stu_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.DO_NOTHING, db_column='dept_id', null=True, blank=True)

    class Meta:
        db_table = 'student'
        managed = False

    def __str__(self):
        return self.name

class Semester(models.Model):
    semester_id = models.AutoField(primary_key=True)
    semester_name = models.CharField(max_length=20)

    class Meta:
        db_table = 'semester'
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
    enroll_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='course_id', null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_column='stu_id', null=True, blank=True)
    semester = models.ForeignKey(Semester, on_delete=models.DO_NOTHING, db_column='semester_id')
    grade = models.FloatField()


    class Meta:
        db_table = 'enrollment'
        managed = False

class Attendance(models.Model):
    attendance_id = models.AutoField(primary_key=True)
    enroll = models.ForeignKey(Enrollment, on_delete=models.CASCADE, db_column='enroll_id')
    attendance_percentage = models.IntegerField()

    class Meta:
        db_table = 'attendance'
        managed = False

    def __str__(self):
        return f"{self.enroll.student.name} - {self.attendance_percentage}%"

class Assessment(models.Model):
    assessment_id = models.AutoField(primary_key=True)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, db_column='enroll_id', null=True, blank=True)
    assessment_type = models.CharField(max_length=50)
    score = models.IntegerField()

    class Meta:
        db_table = 'assessment'
        managed = False

    def __str__(self):
        return f"{self.enrollment.student.name} - Score: {self.score}"

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

class Instructor(models.Model):
    instructor_id = models.AutoField(primary_key=True)
    instructor_name = models.CharField(max_length=100)
    dept_id = models.IntegerField()

    class Meta:
        db_table = 'instructor'
        managed = False


class CourseInstructor(models.Model):
    course_instructor_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, db_column='course_id')
    instructor = models.ForeignKey(Instructor, on_delete=models.DO_NOTHING, db_column='instructor_id')
    semester = models.ForeignKey(Semester, on_delete=models.DO_NOTHING, db_column='semester_id')

    class Meta:
        db_table = 'course_instructor'
        managed = False

class ModelInfo(models.Model):    
    model_name = models.CharField(max_length=255)
    model_encorlabel = models.CharField(max_length=255, default='LabelEncoder')
    model_file = models.CharField(max_length=255)
    training_data = models.CharField(max_length=255, default='learnstyle_dataset.csv')
    training_date = models.DateTimeField()
    model_summary = models.TextField()

    class Meta:    
        db_table = 'modelinfo'  
        managed = True

    def __str__(self):    
        return self.model_name
    

class alfira_ModelInfo(models.Model):
    model_name = models.CharField(max_length=100)
    model_file = models.CharField(max_length=255)
    training_data = models.CharField(max_length=255)
    training_date = models.DateTimeField()
    model_summary = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'AlfiraModelInfo'
        managed = True

    def __str__(self):
        return f"{self.model_name} trained on {self.training_date.strftime('%Y-%m-%d %H:%M:%S')}"
    
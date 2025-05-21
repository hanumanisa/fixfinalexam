from django.core.management.base import BaseCommand
from student_prediction.utils.apriori_rules_hanum import ml_hanum_value

class Command(BaseCommand):
    help = "Generate Apriori rules from course assessment data"
    
    def handle(self, *args, **kwargs):
        try:
            ml_hanum_value()
            self.stdout.write(self.style.SUCCESS('Apriori rules generated and saved to course_apriori_rules.csv!'))
        except FileNotFoundError as e:
            self.stdout.write(self.style.ERROR(str(e)))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating Apriori rules: {str(e)}'))
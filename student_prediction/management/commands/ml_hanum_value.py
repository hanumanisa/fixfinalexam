from django.core.management.base import BaseCommand
from student_prediction.utils.apriori_rules_hanum import ml_hanum_values
import joblib
from student_prediction.models import ModelHanum
from django.utils import timezone

class Command(BaseCommand):
    help = "Generate Apriori rules from course assessment data and log model info"

    def handle(self, *args, **kwargs):
        try:
            rules = ml_hanum_values()
            self.stdout.write(self.style.SUCCESS('Apriori rules generated and saved to course_apriori_rules.csv!'))

            # Simpan rules dataframe ke pickle file
            model_filename = 'apriori_rules_model.pkl'
            joblib.dump(rules, model_filename)
            self.stdout.write(self.style.SUCCESS(f'Apriori rules saved as {model_filename}'))

            # Buat summary hasil training
            report = f"Generated {len(rules)} rules with confidence >= 0.3 and min support >= 0.05."

            # Simpan info ke tabel ModelInfo
            modelhanum = ModelHanum.objects.create(
                model_name='AprioriAlgorithmModel',
                model_file=model_filename,
                training_data='course_example_new.csv',
                training_date=timezone.now(),
                model_summary=report
            )
            self.stdout.write(self.style.SUCCESS(f'Model info saved to DB: ID {modelhanum.id}'))

        except FileNotFoundError as e:
            self.stdout.write(self.style.ERROR(str(e)))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating Apriori rules: {str(e)}'))
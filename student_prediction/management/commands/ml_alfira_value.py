import pandas as pd
from django.core.management.base import BaseCommand
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
import joblib
from student_prediction.models import alfira_ModelInfo
import datetime
from django.utils import timezone


class Command(BaseCommand):
    help = 'Train clustering model KMeans dengan k=3 dan simpan model ke file .pkl'

    def handle(self, *args, **options):
        # Load data
        df = pd.read_csv('all_courses_dataset.csv') 
    
        semester_mapping = {'Semester 1': 0, 'Semester 2': 1, 'Semester 3': 2}
        df['semester_enc'] = df['semester_name'].map(semester_mapping)


        # Encoding difficulty_level (categorical)
        difficulty_mapping = {'Easy': 0, 'Medium': 1, 'Hard': 2}
        df['difficulty_enc'] = df['difficulty_level'].map(difficulty_mapping)


        # Pilih fitur untuk clustering (tambahkan difficulty_enc)
        features = ['avg_grade', 'avg_attendance', 'semester_enc', 'student_count', 'difficulty_enc']
        X = df[features]

        # Clustering KMeans k=3
        kmeans = KMeans(n_clusters=3, random_state=42)
        df['cluster'] = kmeans.fit_predict(X)

        # Simpan hasil cluster ke CSV (opsional)
        df.to_csv('all_courses_clustered.csv', index=False)
        self.stdout.write(self.style.SUCCESS('Clustering result saved to all_courses_clustered.csv'))

        # Simpan model ke file .pkl
        model_filename = 'kmeans_model.pkl'
        joblib.dump(kmeans, model_filename)
        self.stdout.write(self.style.SUCCESS(f'Model saved as {model_filename}'))

        # Simpan info model ke DB, sesuaikan fieldsnya dengan modelmu
        model_info = alfira_ModelInfo.objects.create(
            model_name='KMeansInstructorClustering',
            model_file=model_filename,
            training_data='all_courses_dataset.csv',
             training_date=timezone.now(),
            model_summary='KMeans clustering with k=3 on avg_grade, avg_attendance, semester, student_count, difficulty_level'
        )

        self.stdout.write(self.style.SUCCESS(f'Model info saved to DB: ID {model_info.id}'))

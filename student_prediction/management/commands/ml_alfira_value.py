import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import numpy as np
from django.core.management.base import BaseCommand
import joblib
import datetime
from student_prediction.models import alfira_ModelInfo
from sklearn.decomposition import PCA

def run_clustering(k_list=[2, 3, 4, 5], k_final=3):
    # Baca data CSV
    df = pd.read_csv('all_courses_dataset.csv')  # sesuaikan path/file-nya
    
    # Mapping kategori ke angka
    semester_mapping = {'Semester 1': 0, 'Semester 2': 1, 'Semester 3': 2}
    difficulty_mapping = {'Easy': 0, 'Medium': 1, 'Hard': 2}

    df['semester_enc'] = df['semester_name'].map(semester_mapping).fillna(-1).astype(int)
    df['difficulty_enc'] = df['difficulty_level'].map(difficulty_mapping).fillna(-1).astype(int)

    # Fitur yang dipakai dan bobotnya
    features = ['avg_grade', 'avg_attendance', 'semester_enc', 'student_count', 'difficulty_enc']
    weights = {
        'avg_grade': 3,
        'avg_attendance': 3,
        'semester_enc': 1,
        'difficulty_enc': 3,
        'student_count': 1
    }

    # Ambil data fitur
    X = df[features].copy()

    # Scaling fitur numerik dan kategorikal supaya setara
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    scalerk4 =  'scaler_k4.pkl'
    joblib.dump(scaler, scalerk4)
    
    # Kalikan tiap kolom dengan bobotnya
    for i, feature in enumerate(features):
        X_scaled[:, i] = X_scaled[:, i] * weights[feature]

    silhouette_scores = {}

    # Hitung silhouette score untuk k yang diinginkan
    for k in k_list:
        kmeans = KMeans(n_clusters=k, random_state=42)
        cluster_labels = kmeans.fit_predict(X_scaled)
        silhouette_scores[k] = silhouette_score(X_scaled, cluster_labels)

    # Clustering final k=k_final
    kmeans_final = KMeans(n_clusters=k_final, random_state=42)
    cluster_labels_final = kmeans_final.fit_predict(X_scaled)
    df['cluster'] = cluster_labels_final

    # PCA 2 komponen untuk visualisasi
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    df['pca_1'] = X_pca[:, 0]
    df['pca_2'] = X_pca[:, 1]

    return df, silhouette_scores, kmeans_final

class Command(BaseCommand):
    help = 'Train KMeans clustering with k=4, but show silhouette score k=2 until k=5'

    def handle(self, *args, **options):
        df, silhouette_scores, model = run_clustering(k_list=[2, 3, 4, 5], k_final=4)

        # Simpan data lengkap ke CSV
        df.to_csv('all_courses_clustered_k4.csv', index=False)
        self.stdout.write(self.style.SUCCESS('Clustering results saved to all_courses_clustered_k4.csv'))

        # Simpan model k=4 saja
        model_filename = 'kmeans_model_k4.pkl'
        joblib.dump(model, model_filename)
        self.stdout.write(self.style.SUCCESS(f'Model k=4 saved as {model_filename}'))

        # Simpan silhouette scores ke CSV
        df_scores = pd.DataFrame(list(silhouette_scores.items()), columns=['k', 'silhouette_score'])
        df_scores.to_csv('silhouette_score_k4.csv', index=False)
        self.stdout.write(self.style.SUCCESS('Silhouette scores saved to silhouette_score_k4.csv'))

        # Buat ringkasan silhouette score semua k sekaligus (2 s.d 5)
        scores_text = '; '.join(
            [f'k={k}, silhouette score = {score:.4f}' for k, score in sorted(silhouette_scores.items())]
        )
        model_summary = f'KMeans clustering with {scores_text}. \nI choose K=4.'

        # Simpan info model ke DB (hanya untuk k=3)
        model_info = alfira_ModelInfo.objects.create(
            model_name='KMeansInstructorClustering',
            model_file=model_filename,
            training_data='all_courses_dataset.csv',
            training_date=datetime.datetime.now(),
            model_summary=model_summary
        )
        self.stdout.write(self.style.SUCCESS(f'Model info k=4 saved to DB: ID {model_info.id}'))

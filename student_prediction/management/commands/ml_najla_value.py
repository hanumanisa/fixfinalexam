from django.core.management.base import BaseCommand
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
import joblib
from django.utils import timezone
from student_prediction.models import ModelInfo

class Command(BaseCommand):
    help = 'Train Random Forest model to predict student learning style'

    def handle(self, *args, **kwargs):
        df = pd.read_csv('learnstyle_dataset.csv')

        # Validasi kolom yang diperlukan
        if not {'avg_assessment_score', 'attendance_percentage'}.issubset(df.columns):
            self.stdout.write(self.style.ERROR('Missing required columns in dataset.'))
            return

        def classify_style(row):
            avg = row['avg_assessment_score']
            att = row['attendance_percentage']
            if avg >= 70 and att >= 70:
                return 'smart and diligent'
            elif avg >= 70 and att < 70:
                return 'smart but absent'
            elif avg < 70 and att >= 70:
                return 'diligent but difficult'
            else:
                return 'problematic'

        df['learn_style'] = df.apply(classify_style, axis=1)

        # Persiapan data
        X = df[['avg_assessment_score', 'attendance_percentage']]
        y = df['learn_style']

        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        report = classification_report(y_test, y_pred, target_names=label_encoder.classes_)
        self.stdout.write(self.style.SUCCESS("Classification Report:\n" + report))

        model.fit(X, y_encoded)

        #Save model to file
        model_filename = 'final_learnstyle_model.pkl'
        encoder_filename = 'learnstyle_label_encoder.pkl'

        joblib.dump(model, model_filename)
        joblib.dump(label_encoder, encoder_filename)
        self.stdout.write(self.style.SUCCESS(f'Model and label encoder saved as {model_filename} and {encoder_filename}'))

        # Simpan info ke database
        model_info = ModelInfo.objects.create(
            model_name='RandomForestClassifier - Learn Style',
            model_encorlabel='LabelEncoder',
            model_file=model_filename,
            training_data='learnstyle_dataset.csv',
            training_date=timezone.now(),
            model_summary=report
        )
        self.stdout.write(self.style.SUCCESS(f"Model info berhasil disimpan ke DB. ID: {model_info.id}"))


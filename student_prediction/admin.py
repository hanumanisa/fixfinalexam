from django.contrib import admin
from .models import ModelInfo, alfira_ModelInfo, ModelHanum
from django.utils.html import format_html
from django.utils.timezone import now
from django.urls import path
from django.shortcuts import redirect, get_object_or_404
from django.utils.html import format_html
from django.utils import timezone
from django.contrib import messages
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import joblib
from django.urls import reverse

# Register your models here.
@admin.register(ModelInfo)
class ModelInfoAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'training_date', 'training_data', 'short_summary', 'retrain_button')
    search_fields = ('model_name', 'training_data')

    def short_summary(self, obj):
        return (obj.model_summary[:75] + '...') if obj.model_summary else "-"
    short_summary.short_description = "Summary"

    def retrain_button(self, obj):
        # Gunakan reverse dengan namespace admin dan nama URL yang didefinisikan di get_urls
        url = reverse('admin:student_prediction_modelinfo_retrain_model', args=[obj.pk])
        return format_html('<a class="button" href="{}">Retrain</a>', url)
    retrain_button.short_description = 'Retrain'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'retrain-model/<int:pk>/',
                self.admin_site.admin_view(self.retrain_model_view),
                name='student_prediction_modelinfo_retrain_model'
            ),
        ]
        return custom_urls + urls

    def retrain_model_view(self, request, pk):
        model_info = get_object_or_404(ModelInfo, pk=pk)
        try:
            df = pd.read_csv('learnstyle_dataset.csv')
            required_cols = {'avg_assessment_score', 'attendance_percentage'}
            if not required_cols.issubset(df.columns):
                self.message_user(request, "Dataset tidak memiliki kolom yang diperlukan.", level=messages.ERROR)
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))

            def classify_style(row):
                avg = row['avg_assessment_score']
                att = row['attendance_percentage']
                if avg >= 70 and att >= 70:
                    return 'Smart and Diligent'
                elif avg >= 70 and att < 70:
                    return 'Smart but Absent'
                elif avg < 70 and att >= 70:
                    return 'Diligent but Struggling'
                else:
                    return 'Needs Support'

            df['learn_style'] = df.apply(classify_style, axis=1)

            X = df[['avg_assessment_score', 'attendance_percentage']]
            y = df['learn_style']

            label_encoder = LabelEncoder()
            y_encoded = label_encoder.fit_transform(y)

            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X, y_encoded)

            y_pred = model.predict(X)
            report = classification_report(y_encoded, y_pred, target_names=label_encoder.classes_)

            model_filename = 'final_learnstyle_model.pkl'
            encoder_filename = 'learnstyle_label_encoder.pkl'

            joblib.dump(model, model_filename)
            joblib.dump(label_encoder, encoder_filename)

            model_info.model_file = model_filename
            model_info.training_data = 'learnstyle_dataset.csv'
            model_info.training_date = timezone.now()
            model_info.model_summary = report
            model_info.save()

            self.message_user(request, f'Model berhasil dilatih ulang dan diperbarui (ID: {model_info.id})', level=messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f'Gagal melatih ulang model: {str(e)}', level=messages.ERROR)

        return redirect(request.META.get('HTTP_REFERER', '/admin/'))

@admin.register(alfira_ModelInfo)
class ModelInfoAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'training_date', 'training_data', 'short_summary', 'retrain_button')
    search_fields = ('model_name', 'training_data')

    def short_summary(self, obj):
        return (obj.model_summary[:75] + '...') if obj.model_summary else "-"
    short_summary.short_description = "Summary"

    def retrain_button(self, obj):
        return format_html('<a class="button" href="/admin/retrain-model/{}/">Retrain</a>', obj.id)
    retrain_button.short_description = 'Retrain'



@admin.register(ModelHanum)
class ModelHanumAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'training_date', 'training_data', 'short_summary', 'retrain_button')
    search_fields = ('model_name', 'training_data')

    def short_summary(self, obj):
        return (obj.model_summary[:75] + '...') if obj.model_summary else "-"
    short_summary.short_description = "Summary"

    def retrain_button(self, obj):
        return format_html('<a class="button" href="/admin/retrain-model/{}">Retrain</a>', obj.id)
    retrain_button.short_description = 'Retrain'
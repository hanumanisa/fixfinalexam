from django.urls import path  
from . import views
from . import admin_views
  
app_name = 'student_prediction'  
  
urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'), 
    path('alfira_predictdashboard/', views.cluster_visualization, name='alfira_predictdashboard'),
    path('najla_predictdashboard/', views.najla_predictdashboard, name='najla_predictdashboard'), 
    path('predict-learnstyle/', views.predict_learnstyle, name='predict_learnstyle'),
    path('retrain-model/<int:pk>/', views.retrain_model, name='retrain_model'),
    path('safira_predictdashboard/', views.safira_predictdashboard, name='safira_predictdashboard'),
    path('hanum_predictdashboard/', views.hanum_predictdashboard, name='hanum_predictdashboard'),
    path('get-courses/', views.get_courses, name='get_courses'),
    path('analyze/', views.analyze, name='hanum_analysis'),  
    path('api/instructor_clusters/', views.instructor_clusters_api, name='instructor_clusters_api'),
    path('predict-cluster/', views.predict_cluster, name='predict_cluster'),
]
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from io import BytesIO
import base64
import json
from student_prediction.utils.apriori_rules_hanum import analyze_courses
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import joblib
import numpy as np
from django.conf import settings

from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from .forms import InstructorPerformanceForm


def home(request):
    return render(request, 'student_prediction/home.html')  

def about(request):
    return render(request, 'student_prediction/about.html')  

def alfira_predictdashboard(request):  
    return render(request, 'student_prediction/alfira_predictdashboard.html') 


def instructor_clusters_api(request):
    df = pd.read_csv('all_courses_clustered.csv')  

    cluster_counts = df['cluster'].value_counts().to_dict()

    def get_cluster_points(cluster_num):
        cluster_df = df[df['cluster'] == cluster_num]
        return [{
            'x': row['avg_grade'],
            'y': row['avg_attendance'],
            'instructor': row['instructor_name'],
            'semester': row['semester_name'],
            'total_student': row['student_count'],
            'difficulty': row['difficulty_level'],
        } for _, row in cluster_df.iterrows()]

    response_data = {
        'cluster_0_count': cluster_counts.get(0, 0),
        'cluster_1_count': cluster_counts.get(1, 0),
        'cluster_2_count': cluster_counts.get(2, 0),
        'cluster_0_points': get_cluster_points(0),
        'cluster_1_points': get_cluster_points(1),
        'cluster_2_points': get_cluster_points(2),
    }
    return JsonResponse(response_data)




def load_kmeans_model():
    model_path = os.path.join(settings.BASE_DIR, 'kmeans_model.pkl')
    if not os.path.exists(model_path):
        print("Model file does not exist")
        return None
    try:
        model = joblib.load(model_path)
        print(f"KMeans model loaded: {model}")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None



def predict_cluster(request):
    if request.method == 'POST':
        form = InstructorPerformanceForm(request.POST)
        if form.is_valid():
            print("Cleaned data:", form.cleaned_data)
            try:
                # Get form data
                avg_grade = form.cleaned_data['avg_grade']
                avg_attendance = form.cleaned_data['avg_attendance']
                student_count = form.cleaned_data['total_student']
        
                semester_obj = form.cleaned_data['semester']
                semester_str = semester_obj.semester_name

                difficulty_str = form.cleaned_data['difficulty_level']

                print("Semester name:", semester_str)
                print("Difficulty level:", difficulty_str)

                difficulty_mapping = {
                    "Easy": 0,
                    "Medium": 1,
                    "Hard": 2
                }

                semester_mapping = {
                    "Semester 1": 0,
                    "Semester 2": 1,
                    "Semester 3": 2
                }

                difficulty = difficulty_mapping.get(difficulty_str, -1)
                semester = semester_mapping.get(semester_str, -1)

                if difficulty == -1 or semester == -1:
                    return JsonResponse({
                        'error': 'Invalid difficulty level or semester value',
                        'difficulty_str': difficulty_str,
                        'semester_str': semester_str,
                        'difficulty': difficulty,
                        'semester': semester
                    }, status=400)
            
                input_data = [[
                    avg_grade,
                    avg_attendance,
                    float(semester),
                    student_count,
                    float(difficulty)  
                ]]
                print(f"Input data: {input_data}")
                
                try:
                    print("Trying to load KMeans model...")
                    kmeans = load_kmeans_model()  # <-- Ini model, bukan path
                    if kmeans is None:
                        print("Model loading failed!")
                    else:
                        print(f"Model n_features_in_: {kmeans.n_features_in_}")

                    feature_names = ['avg_grade', 'avg_attendance', 'semester_enc', 'student_count', 'difficulty_enc']
                    # Ubah input_data list jadi DataFrame dengan kolom yang benar
                    input_df = pd.DataFrame(input_data, columns=feature_names)
                    # Lalu prediksi pakai DataFrame
                    cluster = kmeans.predict(input_df)[0]
                    print(f"Predicted cluster: {cluster}")

                    prediction = kmeans.predict(input_df)
                    print(f"Raw prediction output: {prediction}")
                    cluster = prediction[0]
                   
                    cluster_descriptions = {
                        0: "Cluster A",
                        1: "Cluster B",
                        2: "Cluster C",
                    }
                    description = cluster_descriptions.get(cluster, "Unknown cluster")
                    return JsonResponse({
                        'cluster': int(cluster),
                        'description': description,
                        'message': 'Prediction successful'
                    })
                
                except Exception as e:
                    print(f"Error loading model: {e}")
                    return JsonResponse({'error': f'Error loading model: {e}'}, status=500)
            except Exception as e:
                return JsonResponse({
                    'error': f'Unexpected error: {str(e)}'
                }, status=500)
        else:
            print("Form errors:", form.errors)
            return JsonResponse({
                'error': 'Invalid form data',
                'form_errors': form.errors
        }, status=400)            

    else:
        form = InstructorPerformanceForm()

    context = {
        'form': form,
        # Include other context data you need for the visualization
    }
    return render(request, 'student_prediction/alfira_predictdashboard.html', context)




def cluster_visualization(request):
    df = pd.read_csv('all_courses_clustered.csv')

    # Your existing data preparation code...
    cluster_data = df.to_dict('records')
    cluster_counts = df['cluster'].value_counts().to_dict()
    cluster_avgs = df.groupby('cluster').agg({
        'avg_grade': 'mean',
        'avg_attendance': 'mean',
        'student_count': 'mean',
        'semester_enc': 'mean',
        'difficulty_enc': 'mean'  
    }).to_dict('index')

    def get_cluster_points(cluster_num):
        cluster_df = df[df['cluster'] == cluster_num]
        return [{
            'x': row['avg_grade'],
            'y': row['avg_attendance'],
            'instructor': row['instructor_name'],
            'total_student': row['student_count'],
            'semester': row['semester_name'],
            'difficulty': row['difficulty_level']
        } for _, row in cluster_df.iterrows()]

    form = InstructorPerformanceForm()
    
    context = {
        'form': form,
        'cluster_data': cluster_data,
        'cluster_0_count': cluster_counts.get(0, 0),
        'cluster_1_count': cluster_counts.get(1, 0),
        'cluster_2_count': cluster_counts.get(2, 0),
        'cluster_0_avg': cluster_avgs.get(0, {'avg_grade': 0, 'avg_attendance': 0, 'student_count': 0}),
        'cluster_1_avg': cluster_avgs.get(1, {'avg_grade': 0, 'avg_attendance': 0, 'student_count': 0}),
        'cluster_2_avg': cluster_avgs.get(2, {'avg_grade': 0, 'avg_attendance': 0, 'student_count': 0}),
        'cluster_0_points': json.dumps(get_cluster_points(0)),
        'cluster_1_points': json.dumps(get_cluster_points(1)),
        'cluster_2_points': json.dumps(get_cluster_points(2)),
    }

    return render(request, 'student_prediction/alfira_predictdashboard.html', context)













def najla_predictdashboard(request):  
    return render(request, 'student_prediction/najla_predictdashboard.html') 
MODEL_PATH = os.path.join(settings.BASE_DIR, 'final_learnstyle_model.pkl')
ENCODER_PATH = os.path.join(settings.BASE_DIR, 'learnstyle_label_encoder.pkl')

try:
    MODEL = joblib.load(MODEL_PATH)
    LABEL_ENCODER = joblib.load(ENCODER_PATH)
except FileNotFoundError as e:
    MODEL = None
    LABEL_ENCODER = None
    print(f"Model file not found: {e}")

@csrf_exempt
def predict_learnstyle(request):
    if request.method == 'POST':
        if MODEL is None or LABEL_ENCODER is None:
            return JsonResponse({'error': 'Model not loaded.'}, status=500)

        try:
            data = json.loads(request.body)
            name = data.get('name', 'Unknown')
            avg_score = float(data.get('avg_score', 0))
            attendance = float(data.get('attendance', 0))

            input_data = np.array([[avg_score, attendance]])
            prediction_encoded = MODEL.predict(input_data)[0]
            prediction_proba = MODEL.predict_proba(input_data)[0]

            prediction_label = LABEL_ENCODER.inverse_transform([prediction_encoded])[0]

            response = {
                'name': name,
                'prediction': prediction_label,
                'probability': prediction_proba.tolist(),
                'labels': LABEL_ENCODER.classes_.tolist()
            }
            return JsonResponse(response)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def safira_predictdashboard(request):  
    return render(request, 'student_prediction/safira_predictdashboard.html') 

def analysis(request):
    return render(request, 'student_prediction/hanum_analysis.html')

def hanum_predictdashboard(request):
    try:
        assessment_df = pd.read_csv('course_example_new.csv')
        departments = sorted(assessment_df['dept_name'].unique())
        
        initial_dept = request.session.get('selected_department', departments[0] if departments else '')
        
        if initial_dept:
            courses = sorted(assessment_df[assessment_df['dept_name'] == initial_dept]['course_name'].unique())
        else:
            courses = []
            
        context = {
            'departments': departments,
            'courses': courses,
            'selected_department': initial_dept
        }
        
    except FileNotFoundError:
        messages.error(request, "Data file not found. Please run the ETL command first.")
        context = {'departments': [], 'courses': []}
        
    return render(request, 'student_prediction/hanum_predictdashboard.html', context)


def get_courses(request):
    department = request.GET.get('department', '')
    
    try:
        assessment_df = pd.read_csv('course_example_new.csv')
        courses = sorted(assessment_df[assessment_df['dept_name'] == department]['course_name'].unique())
        
        request.session['selected_department'] = department
        
        return HttpResponse(json.dumps(courses), content_type='application/json')
        
    except FileNotFoundError:
        return HttpResponse(json.dumps([]), content_type='application/json')
    

def analyze(request):
    if request.method != 'POST':
        return HttpResponse("Method not allowed", status=405)
    
    department = request.POST.get('department', '')
    course1 = request.POST.get('course1', '')
    course2 = request.POST.get('course2', '')
    
    if not department or not course1 or not course2:
        messages.error(request, "Please select a department and two courses")
        return render(request, 'student_prediction/hanum_predictdashboard.html')
    
    if course1 == course2:
        messages.error(request, "Please select two different courses")
        return render(request, 'student_prediction/hanum_predictdashboard.html')
    
    try:
        assessment_df = pd.read_csv('course_example_new.csv')
        rules_df = pd.read_csv('course_apriori_rules.csv')
        
        result = analyze_courses(department, course1, course2, assessment_df, rules_df)
        
        if 'error' in result:
            messages.error(request, result['error'])
            return render(request, 'student_prediction/hanum_predictdashboard.html')
        
        img_data = create_visualization(result['rule_data'], course1, course2)
        
        departments = sorted(assessment_df['dept_name'].unique())
        courses = sorted(assessment_df[assessment_df['dept_name'] == department]['course_name'].unique())
   
        context = {
            'departments': departments,
            'courses': courses,
            'selected_department': department,
            'analysis_result': result,
            'visualization': img_data
        }
        
        return render(request, 'student_prediction/hanum_analysis.html', context)
        
    except FileNotFoundError:
        messages.error(request, "Data files not found. Please run the ETL and Apriori commands first.")
        return render(request, 'student_prediction/hanum_predictdashboard.html')
    except Exception as e:
        messages.error(request, f"Error analyzing courses: {str(e)}")
        return render(request, 'student_prediction/hanum_predictdashboard.html')

def create_visualization(rule_data, course1, course2):
    """Create visualization of association rules metrics"""
    plt.figure(figsize=(10, 6))
    
    if rule_data is None or rule_data.empty:
        plt.text(0.5, 0.5, f"No association rule found between {course1} and {course2}", 
                horizontalalignment='center', verticalalignment='center')
    else:
        metrics = ['support', 'confidence', 'lift']
        values = [rule_data[metric].values[0] for metric in metrics]
        
        colors = ['#5DA5DA', '#FAA43A', '#60BD68']
        ax = sns.barplot(x=metrics, y=values, palette=colors)
        
        for i, v in enumerate(values):
            ax.text(i, v + 0.02, f'{v:.3f}', ha='center')
        
        plt.title(f'Association Rule Metrics: {course1} and {course2}')
        plt.ylim(0, max(values) * 1.2)  
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight')
    img_buffer.seek(0)
    
    img_data = base64.b64encode(img_buffer.read()).decode('utf-8')
    plt.close()
    
    return img_data








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

def home(request):
    return render(request, 'student_prediction/home.html')  

def about(request):
    return render(request, 'student_prediction/about.html')  

def alfira_predictdashboard(request):  
    return render(request, 'student_prediction/alfira_predictdashboard.html') 

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




from flask import Flask, render_template, request, jsonify
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

# Sample dataset for visualizations
def create_sample_data():
    workout_types = ['Cardio', 'Strength', 'Yoga', 'HIIT', 'Swimming']
    diet_types = ['Vegetarian', 'Vegan', 'Keto', 'Mediterranean', 'Balanced']
    age_groups = ['18-25', '26-35', '36-45', '46-55', '56+']
    
    # Generate sample data
    data = {
        'workout_type': np.random.choice(workout_types, 100),
        'diet_type': np.random.choice(diet_types, 100),
        'age_group': np.random.choice(age_groups, 100),
        'calories_burned': np.random.randint(1500, 3000, 100),
        'bmi': np.random.uniform(18.5, 35, 100)
    }
    return pd.DataFrame(data)

# Health metrics calculations
def calculate_calories_burned(age, weight, height, workout_timing):
    base_calories = (age * 0.2) + (weight * 0.5) + (height * 0.1)
    timing_multiplier = 1 + (workout_timing / 60) * 0.5  # 50% increase per hour
    return base_calories * timing_multiplier

def calculate_bmi(weight, height):
    height_m = height / 100  # Convert cm to meters
    return weight / (height_m ** 2)

def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal Weight"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def generate_suggestions(calories_burned, bmi, workout_type, diet_type, workout_timing):
    suggestions = []
    
    # Calorie burn suggestions
    if calories_burned < 2000:
        suggestions.append("Reduce calorie deficit - current burn rate is below recommended minimum")
    elif calories_burned > 3000:
        suggestions.append("Excellent calorie burn! Maintain this activity level")
    
    # Workout type suggestions
    if workout_type.lower() in ['yoga', 'pilates'] and bmi > 25:
        suggestions.append("Switch to cardio workouts for better results with your profile")
    elif workout_type.lower() == 'strength' and workout_timing < 30:
        suggestions.append("Consider increasing strength training duration for optimal muscle growth")
    
    # Diet suggestions
    if workout_type.lower() in ['strength', 'hiit']:
        suggestions.append("Increase protein intake by 20% based on workout type")
    if diet_type.lower() == 'vegan' and workout_timing > 45:
        suggestions.append("Consider supplementing with plant-based protein sources")
    
    # BMI-based suggestions
    bmi_category = get_bmi_category(bmi)
    if bmi_category == "Underweight":
        suggestions.append("Focus on nutrient-dense foods and strength training to build healthy mass")
    elif bmi_category == "Overweight":
        suggestions.append("Combine cardio exercise with balanced nutrition for sustainable weight loss")
    elif bmi_category == "Obese":
        suggestions.append("Consult healthcare provider for personalized weight management plan")
    
    if not suggestions:
        suggestions.append("Maintain your current healthy lifestyle habits!")
    
    return suggestions

# Visualization functions
def create_calories_chart():
    df = create_sample_data()
    avg_calories = df.groupby('workout_type')['calories_burned'].mean()
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(avg_calories.index, avg_calories.values, color=['#2E8B57', '#3CB371', '#66CDAA', '#98FB98', '#90EE90'])
    plt.title('Average Calories Burned by Workout Type', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Workout Type', fontsize=12)
    plt.ylabel('Average Calories Burned', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.0f}', ha='center', va='bottom')
    
    plt.tight_layout()
    
    # Convert plot to base64 string
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return plot_url

def create_bmi_trends_chart():
    df = create_sample_data()
    bmi_trends = df.groupby('age_group')['bmi'].mean()
    
    plt.figure(figsize=(10, 6))
    plt.plot(bmi_trends.index, bmi_trends.values, marker='o', linewidth=3, markersize=8, color='#2E8B57')
    plt.title('BMI Trends Across Age Groups', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Age Group', fontsize=12)
    plt.ylabel('Average BMI', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Add value labels on points
    for x, y in zip(bmi_trends.index, bmi_trends.values):
        plt.text(x, y + 0.3, f'{y:.1f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return plot_url

def create_diet_distribution_chart():
    df = create_sample_data()
    diet_distribution = df['diet_type'].value_counts()
    
    colors = ['#2E8B57', '#3CB371', '#66CDAA', '#98FB98', '#90EE90']
    
    plt.figure(figsize=(10, 6))
    wedges, texts, autotexts = plt.pie(diet_distribution.values, labels=diet_distribution.index, 
                                      autopct='%1.1f%%', colors=colors, startangle=90)
    plt.title('User Distribution by Diet Type', fontsize=16, fontweight='bold', pad=20)
    
    # Style the autotexts
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return plot_url

@app.route('/')
def dashboard():
    calories_chart = create_calories_chart()
    bmi_chart = create_bmi_trends_chart()
    diet_chart = create_diet_distribution_chart()
    
    return render_template('dashboard.html', 
                         calories_chart=calories_chart,
                         bmi_chart=bmi_chart,
                         diet_chart=diet_chart)

@app.route('/prediction')
def prediction():
    return render_template('prediction.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Get form data
        age = int(request.form['age'])
        weight = float(request.form['weight'])
        height = float(request.form['height'])
        gender = request.form['gender']
        workout_type = request.form['workout_type']
        workout_timing = int(request.form['workout_timing'])
        diet_type = request.form['diet_type']
        
        # Calculate metrics
        calories_burned = calculate_calories_burned(age, weight, height, workout_timing)
        bmi = calculate_bmi(weight, height)
        bmi_category = get_bmi_category(bmi)
        suggestions = generate_suggestions(calories_burned, bmi, workout_type, diet_type, workout_timing)
        
        # Format results
        results = {
            'calories_burned': f"{calories_burned:,.0f}",
            'bmi': f"{bmi:.1f}",
            'bmi_category': bmi_category,
            'suggestions': suggestions,
            'user_data': {
                'age': age,
                'weight': weight,
                'height': height,
                'gender': gender,
                'workout_type': workout_type,
                'workout_timing': workout_timing,
                'diet_type': diet_type
            }
        }
        
        return render_template('results.html', results=results)
        
    except Exception as e:
        return render_template('prediction.html', error=str(e))

# HTML Templates as string variables
base_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HealthFit Pro - Lifestyle Analysis</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-green: #2E8B57;
            --light-green: #98FB98;
            --accent-green: #3CB371;
            --background-light: #F8F9FA;
            --card-white: #FFFFFF;
            --text-dark: #2C3E50;
            --text-light: #6C757D;
        }
        
        body {
            font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: var(--background-light);
            color: var(--text-dark);
            line-height: 1.6;
        }
        
        .sidebar {
            background: linear-gradient(135deg, var(--primary-green), var(--accent-green));
            color: white;
            min-height: 100vh;
            padding: 0;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
        }
        
        .sidebar-brand {
            padding: 2rem 1rem;
            text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .sidebar-brand h3 {
            margin: 0;
            font-weight: 700;
        }
        
        .sidebar-brand i {
            margin-right: 10px;
        }
        
        .nav-link {
            color: rgba(255,255,255,0.9) !important;
            padding: 1rem 1.5rem;
            margin: 0.2rem 1rem;
            border-radius: 0.5rem;
            transition: all 0.3s ease;
        }
        
        .nav-link:hover, .nav-link.active {
            background-color: rgba(255,255,255,0.2);
            color: white !important;
        }
        
        .nav-link i {
            margin-right: 10px;
            width: 20px;
            text-align: center;
        }
        
        .main-content {
            padding: 2rem;
            margin-left: 0;
        }
        
        @media (min-width: 768px) {
            .main-content {
                margin-left: 250px;
            }
        }
        
        .card {
            border: none;
            border-radius: 1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card-header {
            background-color: var(--card-white);
            border-bottom: 2px solid var(--light-green);
            padding: 1.5rem;
            border-radius: 1rem 1rem 0 0 !important;
        }
        
        .card-title {
            color: var(--primary-green);
            font-weight: 700;
            margin: 0;
        }
        
        .health-card {
            background: linear-gradient(135deg, var(--card-white), #F8FFF8);
            border-left: 4px solid var(--primary-green);
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary-green);
            margin: 1rem 0;
        }
        
        .suggestion-item {
            background: var(--light-green);
            border: 1px solid var(--accent-green);
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .btn-primary {
            background-color: var(--primary-green);
            border-color: var(--primary-green);
            padding: 0.75rem 2rem;
            font-weight: 600;
            border-radius: 0.75rem;
        }
        
        .btn-primary:hover {
            background-color: var(--accent-green);
            border-color: var(--accent-green);
            transform: translateY(-2px);
        }
        
        .form-control {
            border-radius: 0.75rem;
            border: 2px solid #E9ECEF;
            padding: 0.75rem 1rem;
            transition: all 0.3s ease;
        }
        
        .form-control:focus {
            border-color: var(--primary-green);
            box-shadow: 0 0 0 0.2rem rgba(46, 139, 87, 0.25);
        }
        
        .chart-container {
            background: var(--card-white);
            padding: 2rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
        }
        
        .stat-badge {
            background-color: var(--light-green);
            color: var(--primary-green);
            padding: 0.5rem 1rem;
            border-radius: 2rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-3 col-lg-2 d-md-block sidebar collapse">
                <div class="sidebar-brand">
                    <h3><i class="fas fa-heartbeat"></i>HealthFit Pro</h3>
                    <p class="text-light mb-0">Lifestyle Analysis Dashboard</p>
                </div>
                <div class="sidebar-sticky pt-3">
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link {{ 'active' if request.endpoint == 'dashboard' }}" href="/">
                                <i class="fas fa-chart-line"></i>
                                Dashboard
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link {{ 'active' if request.endpoint in ['prediction', 'calculate'] }}" href="/prediction">
                                <i class="fas fa-calculator"></i>
                                Health Prediction
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link {{ 'active' if request.endpoint == 'about' }}" href="/about">
                                <i class="fas fa-info-circle"></i>
                                About
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>

            <!-- Main content -->
            <main class="col-md-9 ms-sm-auto col-lg-10 main-content">
                {% block content %}{% endblock %}
            </main>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Add active class management
        document.addEventListener('DOMContentLoaded', function() {
            const currentPath = window.location.pathname;
            const navLinks = document.querySelectorAll('.nav-link');
            
            navLinks.forEach(link => {
                if (link.getAttribute('href') === currentPath) {
                    link.classList.add('active');
                }
            });
        });
    </script>
</body>
</html>
'''

dashboard_html = '''
{% extends "base.html" %}

{% block content %}
<div class="container-fluid">
    <!-- Page Header -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="card health-card">
                <div class="card-body">
                    <h1 class="card-title h3 mb-2"><i class="fas fa-chart-line text-primary"></i> Health & Fitness Dashboard</h1>
                    <p class="text-muted">Comprehensive analysis of health metrics and lifestyle patterns</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Charts Row 1 -->
    <div class="row">
        <div class="col-lg-8">
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title"><i class="fas fa-fire text-danger"></i> Average Calories Burned by Workout Type</h3>
                </div>
                <div class="card-body">
                    <div class="chart-container">
                        <img src="data:image/png;base64,{{ calories_chart }}" alt="Calories Burned by Workout Type" class="img-fluid">
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-lg-4">
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title"><i class="fas fa-utensils text-success"></i> User Distribution by Diet Type</h3>
                </div>
                <div class="card-body">
                    <div class="chart-container">
                        <img src="data:image/png;base64,{{ diet_chart }}" alt="Diet Type Distribution" class="img-fluid">
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Charts Row 2 -->
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title"><i class="fas fa-weight-scale text-info"></i> BMI Trends Across Age Groups</h3>
                </div>
                <div class="card-body">
                    <div class="chart-container">
                        <img src="data:image/png;base64,{{ bmi_chart }}" alt="BMI Trends by Age Group" class="img-fluid">
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Statistics Cards -->
    <div class="row">
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <i class="fas fa-users fa-2x text-primary mb-3"></i>
                    <h4 class="metric-value">1,247</h4>
                    <p class="text-muted">Active Users</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <i class="fas fa-fire fa-2x text-danger mb-3"></i>
                    <h4 class="metric-value">2,350</h4>
                    <p class="text-muted">Avg Calories/Day</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <i class="fas fa-weight-scale fa-2x text-info mb-3"></i>
                    <h4 class="metric-value">24.8</h4>
                    <p class="text-muted">Avg BMI</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <i class="fas fa-heart fa-2x text-success mb-3"></i>
                    <h4 class="metric-value">78%</h4>
                    <p class="text-muted">Healthy Profiles</p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

prediction_html = '''
{% extends "base.html" %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="card health-card">
                <div class="card-body">
                    <h1 class="card-title h3 mb-2"><i class="fas fa-calculator text-primary"></i> Health Prediction Analysis</h1>
                    <p class="text-muted">Enter your lifestyle data to receive personalized health insights and recommendations</p>
                </div>
            </div>
        </div>
    </div>

    <div class="row justify-content-center">
        <div class="col-lg-8">
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title"><i class="fas fa-user-circle"></i> Personal Information</h3>
                </div>
                <div class="card-body">
                    {% if error %}
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        <i class="fas fa-exclamation-triangle"></i> {{ error }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                    {% endif %}
                    
                    <form method="POST" action="/calculate">
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="age" class="form-label">Age</label>
                                <input type="number" class="form-control" id="age" name="age" required min="18" max="100">
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="gender" class="form-label">Gender</label>
                                <select class="form-control" id="gender" name="gender" required>
                                    <option value="">Select Gender</option>
                                    <option value="male">Male</option>
                                    <option value="female">Female</option>
                                    <option value="other">Other</option>
                                </select>
                            </div>
                        </div>

                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="weight" class="form-label">Weight (kg)</label>
                                <input type="number" class="form-control" id="weight" name="weight" required min="30" max="200" step="0.1">
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="height" class="form-label">Height (cm)</label>
                                <input type="number" class="form-control" id="height" name="height" required min="100" max="250">
                            </div>
                        </div>

                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="workout_type" class="form-label">Workout Type</label>
                                <select class="form-control" id="workout_type" name="workout_type" required>
                                    <option value="">Select Workout Type</option>
                                    <option value="Cardio">Cardio</option>
                                    <option value="Strength">Strength Training</option>
                                    <option value="Yoga">Yoga/Pilates</option>
                                    <option value="HIIT">HIIT</option>
                                    <option value="Swimming">Swimming</option>
                                    <option value="Cycling">Cycling</option>
                                </select>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="workout_timing" class="form-label">Workout Timing (minutes)</label>
                                <input type="number" class="form-control" id="workout_timing" name="workout_timing" required min="10" max="180">
                            </div>
                        </div>

                        <div class="row">
                            <div class="col-12 mb-4">
                                <label for="diet_type" class="form-label">Diet Type</label>
                                <select class="form-control" id="diet_type" name="diet_type" required>
                                    <option value="">Select Diet Type</option>
                                    <option value="Vegetarian">Vegetarian</option>
                                    <option value="Vegan">Vegan</option>
                                    <option value="Keto">Keto</option>
                                    <option value="Mediterranean">Mediterranean</option>
                                    <option value="Balanced">Balanced</option>
                                    <option value="Low Carb">Low Carb</option>
                                    <option value="High Protein">High Protein</option>
                                </select>
                            </div>
                        </div>

                        <div class="text-center">
                            <button type="submit" class="btn btn-primary btn-lg">
                                <i class="fas fa-chart-bar"></i> Calculate Health Metrics
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

results_html = '''
{% extends "base.html" %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="card health-card">
                <div class="card-body">
                    <h1 class="card-title h3 mb-2"><i class="fas fa-chart-bar text-primary"></i> Health Analysis Results</h1>
                    <p class="text-muted">Personalized insights based on your lifestyle data</p>
                </div>
            </div>
        </div>
    </div>

    <!-- User Data Summary -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title"><i class="fas fa-user-check"></i> Your Profile Summary</h3>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-2 text-center">
                            <span class="stat-badge">Age: {{ results.user_data.age }}</span>
                        </div>
                        <div class="col-md-2 text-center">
                            <span class="stat-badge">Weight: {{ results.user_data.weight }}kg</span>
                        </div>
                        <div class="col-md-2 text-center">
                            <span class="stat-badge">Height: {{ results.user_data.height }}cm</span>
                        </div>
                        <div class="col-md-2 text-center">
                            <span class="stat-badge">{{ results.user_data.gender|title }}</span>
                        </div>
                        <div class="col-md-2 text-center">
                            <span class="stat-badge">{{ results.user_data.workout_type }}</span>
                        </div>
                        <div class="col-md-2 text-center">
                            <span class="stat-badge">{{ results.user_data.diet_type }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Health Metrics -->
    <div class="row">
        <div class="col-md-4">
            <div class="card text-center h-100">
                <div class="card-body">
                    <i class="fas fa-fire fa-3x text-danger mb-3"></i>
                    <h4 class="card-title">Calories Burned</h4>
                    <div class="metric-value">{{ results.calories_burned }} kcal</div>
                    <p class="text-muted">Estimated daily calorie expenditure</p>
                </div>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="card text-center h-100">
                <div class="card-body">
                    <i class="fas fa-weight-scale fa-3x text-info mb-3"></i>
                    <h4 class="card-title">Body Mass Index</h4>
                    <div class="metric-value">{{ results.bmi }}</div>
                    <p class="text-muted">{{ results.bmi_category }}</p>
                </div>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="card text-center h-100">
                <div class="card-body">
                    <i class="fas fa-clock fa-3x text-warning mb-3"></i>
                    <h4 class="card-title">Workout Duration</h4>
                    <div class="metric-value">{{ results.user_data.workout_timing }} min</div>
                    <p class="text-muted">Daily exercise time</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Personalized Suggestions -->
    <div class="row mt-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title"><i class="fas fa-lightbulb text-warning"></i> Personalized Health Suggestions</h3>
                </div>
                <div class="card-body">
                    {% for suggestion in results.suggestions %}
                    <div class="suggestion-item">
                        <i class="fas fa-check-circle text-success me-2"></i>
                        {{ suggestion }}
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>

    <!-- Action Buttons -->
    <div class="row mt-4">
        <div class="col-12 text-center">
            <a href="/prediction" class="btn btn-primary me-3">
                <i class="fas fa-redo"></i> New Analysis
            </a>
            <a href="/" class="btn btn-outline-primary">
                <i class="fas fa-chart-line"></i> View Dashboard
            </a>
        </div>
    </div>
</div>
{% endblock %}
'''

about_html = '''
{% extends "base.html" %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="card health-card">
                <div class="card-body">
                    <h1 class="card-title h3 mb-2"><i class="fas fa-info-circle text-primary"></i> About HealthFit Pro</h1>
                    <p class="text-muted">Comprehensive lifestyle analysis and health prediction platform</p>
                </div>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-lg-8">
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title"><i class="fas fa-rocket"></i> Our Mission</h3>
                </div>
                <div class="card-body">
                    <p>HealthFit Pro is an advanced lifestyle analysis platform designed to provide personalized health insights and recommendations based on your unique profile and habits.</p>
                    
                    <h5 class="mt-4">Key Features:</h5>
                    <ul class="list-group list-group-flush">
                        <li class="list-group-item">
                            <i class="fas fa-chart-bar text-primary me-2"></i>
                            <strong>Comprehensive Dashboard:</strong> Visualize health trends and patterns
                        </li>
                        <li class="list-group-item">
                            <i class="fas fa-calculator text-success me-2"></i>
                            <strong>Advanced Calculations:</strong> Accurate BMI and calorie expenditure analysis
                        </li>
                        <li class="list-group-item">
                            <i class="fas fa-lightbulb text-warning me-2"></i>
                            <strong>Personalized Suggestions:</strong> Tailored recommendations for your lifestyle
                        </li>
                        <li class="list-group-item">
                            <i class="fas fa-database text-info me-2"></i>
                            <strong>Data-Driven Insights:</strong> Based on comprehensive health metrics
                        </li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="col-lg-4">
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title"><i class="fas fa-calculator"></i> Health Metrics</h3>
                </div>
                <div class="card-body">
                    <h6>BMI Categories:</h6>
                    <ul class="list-unstyled">
                        <li><span class="badge bg-success">Under 18.5</span> Underweight</li>
                        <li><span class="badge bg-primary">18.5 - 24.9</span> Normal</li>
                        <li><span class="badge bg-warning">25 - 29.9</span> Overweight</li>
                        <li><span class="badge bg-danger">30+</span> Obese</li>
                    </ul>
                    
                    <h6 class="mt-3">Calorie Targets:</h6>
                    <ul class="list-unstyled">
                        <li><i class="fas fa-fire text-danger"></i> <strong>Sedentary:</strong> 1,800-2,000 kcal</li>
                        <li><i class="fas fa-fire text-warning"></i> <strong>Active:</strong> 2,000-2,500 kcal</li>
                        <li><i class="fas fa-fire text-success"></i> <strong>Athlete:</strong> 2,500-3,000+ kcal</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

# Create template routes
@app.route('/base')
def base_template():
    return base_html

@app.route('/template/dashboard')
def dashboard_template():
    return dashboard_html

@app.route('/template/prediction')
def prediction_template():
    return prediction_html

@app.route('/template/results')
def results_template():
    return results_html

@app.route('/template/about')
def about_template():
    return about_html

# Function to create templates directory and files
def create_template_files():
    templates_dir = 'templates'
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Write template files
    with open(os.path.join(templates_dir, 'base.html'), 'w') as f:
        f.write(base_html)
    with open(os.path.join(templates_dir, 'dashboard.html'), 'w') as f:
        f.write(dashboard_html)
    with open(os.path.join(templates_dir, 'prediction.html'), 'w') as f:
        f.write(prediction_html)
    with open(os.path.join(templates_dir, 'results.html'), 'w') as f:
        f.write(results_html)
    with open(os.path.join(templates_dir, 'about.html'), 'w') as f:
        f.write(about_html)

if __name__ == '__main__':
    # Create template files
    create_template_files()
    
    # Try to setup ngrok if available
    try:
        from pyngrok import ngrok
        public_url = ngrok.connect(5000)
        print(f" * ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:5000\"")
    except ImportError:
        print(" * pyngrok not installed. Running without tunnel.")
        print(" * Install with: pip install pyngrok")
    
    print(" * Starting HealthFit Pro Application...")
    print(" * Access the application at: http://127.0.0.1:5000")
    print(" * Or use the ngrok URL above if available")
    
    app.run(debug=True,use_reloader=False, host='0.0.0.0', port=5000)
    
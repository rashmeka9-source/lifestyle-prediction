# =====================================================
# 🩺 HealthFit Pro - Streamlit Version
# =====================================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------
# Sample Dataset Generator
# ---------------------------
def create_sample_data():
    workout_types = ['Cardio', 'Strength', 'Yoga', 'HIIT', 'Swimming']
    diet_types = ['Vegetarian', 'Vegan', 'Keto', 'Mediterranean', 'Balanced']
    age_groups = ['18-25', '26-35', '36-45', '46-55', '56+']

    data = {
        'workout_type': np.random.choice(workout_types, 100),
        'diet_type': np.random.choice(diet_types, 100),
        'age_group': np.random.choice(age_groups, 100),
        'calories_burned': np.random.randint(1500, 3000, 100),
        'bmi': np.random.uniform(18.5, 35, 100)
    }
    return pd.DataFrame(data)

# ---------------------------
# Health Calculations
# ---------------------------
def calculate_calories_burned(age, weight, height, workout_timing):
    base_calories = (age * 0.2) + (weight * 0.5) + (height * 0.1)
    timing_multiplier = 1 + (workout_timing / 60) * 0.5
    return base_calories * timing_multiplier

def calculate_bmi(weight, height):
    height_m = height / 100
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

    if calories_burned < 2000:
        suggestions.append("Reduce calorie deficit - current burn rate is below recommended minimum.")
    elif calories_burned > 3000:
        suggestions.append("Excellent calorie burn! Maintain this activity level.")

    if workout_type.lower() in ['yoga', 'pilates'] and bmi > 25:
        suggestions.append("Switch to cardio workouts for better results with your profile.")
    elif workout_type.lower() == 'strength' and workout_timing < 30:
        suggestions.append("Increase strength training duration for optimal muscle growth.")

    if workout_type.lower() in ['strength', 'hiit']:
        suggestions.append("Increase protein intake by 20% based on workout type.")
    if diet_type.lower() == 'vegan' and workout_timing > 45:
        suggestions.append("Consider supplementing with plant-based protein sources.")

    bmi_category = get_bmi_category(bmi)
    if bmi_category == "Underweight":
        suggestions.append("Focus on nutrient-dense foods and strength training to build healthy mass.")
    elif bmi_category == "Overweight":
        suggestions.append("Combine cardio exercise with balanced nutrition for sustainable weight loss.")
    elif bmi_category == "Obese":
        suggestions.append("Consult a healthcare provider for a personalized weight management plan.")

    if not suggestions:
        suggestions.append("Maintain your current healthy lifestyle habits!")

    return suggestions

# ---------------------------
# Visualization Functions
# ---------------------------
def create_calories_chart():
    df = create_sample_data()
    avg_calories = df.groupby('workout_type')['calories_burned'].mean()
    fig, ax = plt.subplots(figsize=(8,5))
    bars = ax.bar(avg_calories.index, avg_calories.values, color=['#2E8B57','#3CB371','#66CDAA','#98FB98','#90EE90'])
    ax.set_title("Average Calories Burned by Workout Type", fontsize=14, fontweight='bold')
    ax.set_xlabel("Workout Type")
    ax.set_ylabel("Average Calories Burned")
    ax.grid(axis='y', alpha=0.3)
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height(), f'{bar.get_height():.0f}', ha='center', va='bottom')
    st.pyplot(fig)

def create_bmi_trends_chart():
    df = create_sample_data()
    bmi_trends = df.groupby('age_group')['bmi'].mean()
    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(bmi_trends.index, bmi_trends.values, marker='o', color='#2E8B57', linewidth=3)
    ax.set_title("BMI Trends Across Age Groups", fontsize=14, fontweight='bold')
    ax.set_xlabel("Age Group")
    ax.set_ylabel("Average BMI")
    ax.grid(True, alpha=0.3)
    for x, y in zip(bmi_trends.index, bmi_trends.values):
        ax.text(x, y+0.3, f'{y:.1f}', ha='center', va='bottom', fontweight='bold')
    st.pyplot(fig)

def create_diet_distribution_chart():
    df = create_sample_data()
    diet_distribution = df['diet_type'].value_counts()
    fig, ax = plt.subplots(figsize=(6,6))
    wedges, texts, autotexts = ax.pie(
        diet_distribution.values, labels=diet_distribution.index, autopct='%1.1f%%',
        colors=['#2E8B57','#3CB371','#66CDAA','#98FB98','#90EE90'], startangle=90
    )
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    ax.set_title("User Distribution by Diet Type", fontsize=14, fontweight='bold')
    st.pyplot(fig)

# ---------------------------
# Streamlit App
# ---------------------------
st.set_page_config(page_title="HealthFit Pro", layout="wide")
st.sidebar.title("🏋️‍♂️ HealthFit Pro")
st.sidebar.markdown("### Lifestyle Analysis & Prediction")

page = st.sidebar.radio("Navigate", ["🏠 Dashboard", "📊 Health Prediction", "ℹ️ About"])

# ---------------------------
# Dashboard Page
# ---------------------------
if page == "🏠 Dashboard":
    st.title("📈 Health & Fitness Dashboard")
    st.markdown("Comprehensive analysis of health metrics and lifestyle patterns.")

    col1, col2 = st.columns([2,1])
    with col1:
        create_calories_chart()
    with col2:
        create_diet_distribution_chart()

    create_bmi_trends_chart()

    st.markdown("### Key Statistics")
    cols = st.columns(4)
    metrics = [("Active Users","1,247"),("Avg Calories/Day","2,350"),("Avg BMI","24.8"),("Healthy Profiles","78%")]
    for col, (title, value) in zip(cols, metrics):
        col.metric(title, value)

# ---------------------------
# Prediction Page
# ---------------------------
elif page == "📊 Health Prediction":
    st.title("🧮 Health Prediction Analysis")
    st.markdown("Enter your lifestyle data to get personalized health insights.")

    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", 10, 100, 25)
            weight = st.number_input("Weight (kg)", 30.0, 200.0, 70.0)
            height = st.number_input("Height (cm)", 100.0, 220.0, 170.0)
            gender = st.selectbox("Gender", ["Male","Female","Other"])
        with col2:
            workout_type = st.selectbox("Workout Type", ["Cardio","Strength","Yoga","HIIT","Swimming"])
            workout_timing = st.slider("Workout Duration (minutes)", 10, 120, 45)
            diet_type = st.selectbox("Diet Type", ["Vegetarian","Vegan","Keto","Mediterranean","Balanced"])
        submit = st.form_submit_button("🔍 Analyze My Health")

    if submit:
        calories_burned = calculate_calories_burned(age, weight, height, workout_timing)
        bmi = calculate_bmi(weight, height)
        bmi_category = get_bmi_category(bmi)
        suggestions = generate_suggestions(calories_burned, bmi, workout_type, diet_type, workout_timing)

        st.subheader("📊 Your Health Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Calories Burned", f"{calories_burned:,.0f} kcal")
        col2.metric("BMI", f"{bmi:.1f}")
        col3.metric("BMI Category", bmi_category)

        st.subheader("💡 Personalized Suggestions")
        for s in suggestions:
            st.success(f"✅ {s}")

# ---------------------------
# About Page
# ---------------------------
elif page == "ℹ️ About":
    st.title("About HealthFit Pro")
    st.markdown("""
**HealthFit Pro** is an intelligent health analytics tool that visualizes workout & diet data,
predicts calories burned and BMI, and provides actionable health insights.

**Features:**
- 🧠 AI-based calorie and BMI predictions  
- 📊 Dynamic charts for fitness trends  
- 💬 Personalized lifestyle suggestions  
- 🥗 Multi-diet & workout pattern analytics
""")

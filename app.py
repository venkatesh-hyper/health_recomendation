import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)
    return client

def save_to_google_sheets(data):
    client = authenticate_google_sheets()
    sheet = client.open("working_model_data").sheet1  
    sheet.append_row(data)

def calculate_metrics(weight, height, age, waist, neck, gender, activity_level, bone_density):
    bmi = weight / (height ** 2)
    if gender == 'Male':
        bfp = (1.20 * bmi) + (0.23 * age) - 16.2
        bmr = (10 * weight) + (6.25 * height * 100) - (5 * age) + 5
    else:
        hip = st.number_input("Enter your hip circumference (cm)", min_value=0.0, format="%.2f")
        bfp = (1.20 * bmi) + (0.23 * age) - 5.4
        bmr = (10 * weight) + (6.25 * height * 100) - (5 * age) - 161
    tdee = bmr * activity_level
    whtr = waist / (height * 100)
    risk_level = "High risk" if whtr >= 0.5 else "Low risk"
    ideal_weight = 50 + (2.3 * ((height * 100 / 2.54) - 60)) if gender == 'Male' else 45.5 + (2.3 * ((height * 100 / 2.54) - 60))
    metabolic_age = (bmr / 1500) * age
    t_score = (bone_density - 1.2) / 0.1
    return [bmi, bfp, bmr, tdee, whtr, risk_level, ideal_weight, metabolic_age, t_score]

def main():
    st.title("Health Metrics Predictor")
    username = st.text_input("Enter your name")
    age = st.number_input("Enter your age", min_value=0, format="%d")
    weight = st.number_input("Enter your weight (kg)", min_value=0.0, format="%.2f")
    height = st.number_input("Enter your height (m)", min_value=0.0, format="%.2f")
    waist = st.number_input("Enter your waist circumference (cm)", min_value=0.0, format="%.2f")
    neck = st.number_input("Enter your neck circumference (cm)", min_value=0.0, format="%.2f")
    gender = st.radio("Select Gender", ('Male', 'Female'))
    activity_level = st.selectbox("Select Activity Level", [1.2, 1.375, 1.55, 1.725], format_func=lambda x: f"{x}x Basal Metabolic Rate")
    bone_density = st.number_input("Enter your bone density (g/cm^2)", min_value=0.0, format="%.2f")
    
    if st.button("Calculate Metrics"):
        results = calculate_metrics(weight, height, age, waist, neck, gender, activity_level, bone_density)
        bmi, bfp, bmr, tdee, whtr, risk_level, ideal_weight, metabolic_age, t_score = results
        
        st.subheader("Results")
        st.write(f"**BMI:** {bmi:.2f}")
        st.write(f"**Body Fat Percentage:** {bfp:.2f}%")
        st.write(f"**BMR:** {bmr:.2f} kcal/day")
        st.write(f"**TDEE:** {tdee:.2f} kcal/day")
        st.write(f"**Waist-to-Height Ratio:** {whtr:.2f} ({risk_level})")
        st.write(f"**Ideal Body Weight:** {ideal_weight:.2f} kg")
        st.write(f"**Metabolic Age:** {metabolic_age:.2f} years")
        st.write(f"**T-Score (Bone Density Prediction):** {t_score:.2f}")
        
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_data = [username, age, weight, height, waist, neck, gender, activity_level, bone_density, *results, current_time]
        save_to_google_sheets(user_data)
        st.success("Data saved successfully!")

if __name__ == "__main__":
    main()
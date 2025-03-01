import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import matplotlib.pyplot as plt
import numpy as np

# Authenticate Google Sheets
def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)
    return client

# Save data to Google Sheets
def save_to_google_sheets(data):
    client = authenticate_google_sheets()
    sheet = client.open("working_model_data").sheet1  
    sheet.append_row(data)

# Load previous data
def load_previous_data():
    client = authenticate_google_sheets()
    sheet = client.open("working_model_data").sheet1  
    records = sheet.get_all_records()
    return pd.DataFrame(records) if records else pd.DataFrame()

# Calculate Health Metrics
def calculate_metrics(weight, height, age, waist, neck, gender, activity_level, bone_density, sleep_hours, water_intake, hip=None):
    bmi = weight / (height ** 2)
    
    if gender == 'Male':
        bfp = (1.20 * bmi) + (0.23 * age) - 16.2
        bmr = (10 * weight) + (6.25 * height * 100) - (5 * age) + 5
    else:
        bfp = (1.20 * bmi) + (0.23 * age) - 5.4
        bmr = (10 * weight) + (6.25 * height * 100) - (5 * age) - 161

    tdee = bmr * activity_level
    whtr = waist / (height * 100)
    risk_level = "High risk" if whtr >= 0.5 else "Low risk"

    ideal_weight = 50 + (2.3 * ((height * 100 / 2.54) - 60)) if gender == 'Male' else 45.5 + (2.3 * ((height * 100 / 2.54) - 60))
    lbm = weight * (1 - (bfp / 100))  # Lean Body Mass
    metabolic_age = (bmr / 1500) * age

    avg_bone_density = 1.2  # Placeholder value
    t_score = (bone_density - avg_bone_density) / 0.1  # Bone health prediction

    weight_loss_deficit = tdee - 500  # Recommended caloric intake for weight loss
    
    # Macronutrient Recommendations (Based on TDEE)
    protein = weight * 2.2  # 2.2g per kg of body weight
    carbs = (tdee * 0.5) / 4  # 50% of calories from carbs
    fats = (tdee * 0.3) / 9  # 30% of calories from fats

    # Hydration Check
    hydration_status = "Adequate" if water_intake >= 2.7 else "Low"

    # Sleep Check
    sleep_status = "Good" if sleep_hours >= 7 else "Needs Improvement"

    return [bmi, bfp, lbm, bmr, tdee, whtr, risk_level, ideal_weight, metabolic_age, t_score, weight_loss_deficit, protein, carbs, fats, hydration_status, sleep_status]

# Streamlit UI
def main():
    st.title("💪 Advanced Health Metrics & Wellness Tracker")

    # User Inputs
    username = st.text_input("Enter your name")
    age = st.number_input("Enter your age", min_value=0, format="%d")
    weight = st.number_input("Enter your weight (kg)", min_value=0.0, format="%.2f")
    height = st.number_input("Enter your height (m)", min_value=0.0, format="%.2f")
    waist = st.number_input("Enter your waist circumference (cm)", min_value=0.0, format="%.2f")
    neck = st.number_input("Enter your neck circumference (cm)", min_value=0.0, format="%.2f")
    gender = st.radio("Select Gender", ('Male', 'Female'))
    activity_level = st.selectbox("Select Activity Level", [1.2, 1.375, 1.55, 1.725], format_func=lambda x: f"{x}x Basal Metabolic Rate")
    bone_density = st.number_input("Enter your bone density (g/cm^2)", min_value=0.0, format="%.2f")
    sleep_hours = st.slider("Sleep Duration (Hours)", 0, 12, 7)
    water_intake = st.slider("Daily Water Intake (Liters)", 0.0, 5.0, 2.5)

    hip = None
    if gender == "Female":
        hip = st.number_input("Enter your hip circumference (cm)", min_value=0.0, format="%.2f")

    if st.button("📊 Calculate & Analyze"):
        results = calculate_metrics(weight, height, age, waist, neck, gender, activity_level, bone_density, sleep_hours, water_intake, hip)
        bmi, bfp, lbm, bmr, tdee, whtr, risk_level, ideal_weight, metabolic_age, t_score, weight_loss_deficit, protein, carbs, fats, hydration_status, sleep_status = results
        
        st.subheader("📌 Your Health Metrics")
        st.metric("BMI", f"{bmi:.2f}")
        st.metric("Body Fat Percentage", f"{bfp:.2f}%")
        st.metric("Lean Body Mass", f"{lbm:.2f} kg")
        st.metric("Basal Metabolic Rate", f"{bmr:.2f} kcal/day")
        st.metric("Total Daily Energy Expenditure", f"{tdee:.2f} kcal/day")
        st.metric("Waist-to-Height Ratio", f"{whtr:.2f} ({risk_level})")
        st.metric("Metabolic Age", f"{metabolic_age:.2f} years")
        st.metric("T-Score (Bone Density)", f"{t_score:.2f}")
        st.metric("Hydration Status", hydration_status)
        st.metric("Sleep Quality", sleep_status)

        st.subheader("🍽 Nutrition Plan")
        st.write(f"**Recommended Daily Macros:**")
        st.write(f"- **Protein:** {protein:.2f}g")
        st.write(f"- **Carbohydrates:** {carbs:.2f}g")
        st.write(f"- **Fats:** {fats:.2f}g")

        # Save data to Google Sheets
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_data = [username, age, weight, height, waist, neck, gender, activity_level, bone_density, *results, current_time]
        save_to_google_sheets(user_data)
        st.success("✅ Data saved successfully!")

        # Load & Visualize Previous Data
        df = load_previous_data()
        if not df.empty:
            st.subheader("📈 Progress Over Time")
            fig, ax = plt.subplots()
            ax.plot(df['BMI'], label="BMI", marker="o")
            ax.plot(df['Body Fat Percentage'], label="BFP", marker="s")
            ax.set_xlabel("Entries")
            ax.set_ylabel("Value")
            ax.legend()
            st.pyplot(fig)

if __name__ == "__main__":
    main()

import math
import datetime

def get_float_input(prompt, min_value=0):
    while True:
        try:
            value = float(input(prompt))
            if value <= min_value:
                print(f"Invalid input. Value must be greater than {min_value}.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_valid_gender():
    while True:
        gender = input("Enter your gender (M/F): ").strip().upper()
        if gender in ['M', 'F']:
            return gender
        print("Invalid input. Please enter 'M' or 'F'.")

def get_valid_activity_level():
    activity_levels = {"1": 1.2, "2": 1.375, "3": 1.55, "4": 1.725}
    while True:
        print("Select Activity Level:\n1. Sedentary (Little to no exercise)\n2. Lightly active (1-3 days/week)\n3. Moderately active (3-5 days/week)\n4. Very active (6-7 days/week)")
        choice = input("Enter the number corresponding to your activity level: ").strip()
        if choice in activity_levels:
            return activity_levels[choice]
        print("Invalid input. Please select a valid option.")

def calculate_metrics():
    results = []
    
    # User details
    username = input("Enter your name: ").strip()
    age = int(get_float_input("Enter your age: ", min_value=0))
    
    weight = get_float_input("Enter your weight (kg): ", min_value=0)
    height = get_float_input("Enter your height (m): ", min_value=0)
    
    bmi = weight / (height ** 2)
    results.append(f"BMI: {bmi:.2f}")
    
    waist = get_float_input("Enter your waist circumference (cm): ", min_value=0)
    neck = get_float_input("Enter your neck circumference (cm): ", min_value=0)
    gender = get_valid_gender()
    
    if gender == 'F':
        hip = get_float_input("Enter your hip circumference (cm): ", min_value=0)
    
    # Body Fat Percentage Calculation (New Method)
    if gender == 'M':
        bfp = (1.20 * bmi) + (0.23 * age) - 16.2
    else:
        bfp = (1.20 * bmi) + (0.23 * age) - 5.4
    
    results.append(f"Body Fat Percentage: {bfp:.2f}%")
    
    lbm = weight * (1 - (bfp / 100))
    results.append(f"Lean Body Mass: {lbm:.2f} kg")
    
    if gender == 'F':
        bmr = (10 * weight) + (6.25 * height * 100) - (5 * age) - 161
    else:
        bmr = (10 * weight) + (6.25 * height * 100) - (5 * age) + 5
    results.append(f"BMR: {bmr:.2f} kcal/day")
    
    tdee = bmr * get_valid_activity_level()
    results.append(f"TDEE: {tdee:.2f} kcal/day")
    
    whtr = waist / (height * 100)
    risk_level = "High risk" if whtr >= 0.5 else "Low risk"
    results.append(f"Waist-to-Height Ratio (WHtR): {whtr:.2f} ({risk_level})")
    
    if gender == 'F':
        ideal_weight = 45.5 + (2.3 * ((height * 100 / 2.54) - 60))
    else:
        ideal_weight = 50 + (2.3 * ((height * 100 / 2.54) - 60))
    results.append(f"Ideal Body Weight: {ideal_weight:.2f} kg")
    
    avg_bmr_for_age = 1500  # Placeholder value
    metabolic_age = (bmr / avg_bmr_for_age) * age
    results.append(f"Metabolic Age: {metabolic_age:.2f} years")
    
    avg_bone_density = 1.2  # Placeholder value
    bone_density = get_float_input("Enter your bone density (g/cm^2): ", min_value=0)
    bone_density_sd = 0.1  # Placeholder value
    t_score = (bone_density - avg_bone_density) / bone_density_sd
    results.append(f"T-Score (Bone Density Prediction): {t_score:.2f}")
    
    weight_loss_deficit = tdee - 500
    results.append(f"Caloric Intake for Weight Loss: {weight_loss_deficit:.2f} kcal/day")
    
    recommendations = []
    if bmi > 25:
        recommendations.append("Consider reducing calorie intake and increasing physical activity to lower BMI.")
    elif bmi < 18.5:
        recommendations.append("Increase nutrient-dense food intake to reach a healthy weight.")
    
    if bfp > 25 and gender == 'M' or bfp > 32 and gender == 'F':
        recommendations.append("Consider incorporating strength training and a balanced diet to reduce body fat.")
    
    if t_score < -2.5:
        recommendations.append("High risk of osteoporosis. Consult a healthcare professional for bone health strategies.")
    
    if whtr >= 0.5:
        recommendations.append("Increased risk of cardiovascular diseases. Maintain a healthy waist size.")
    
    current_time = datetime.datetime.now().strftime("%H-%M-%S_%d-%m-%Y")
    filename = f"{username}_{age}_{current_time}.txt"
    
    try:
        with open(filename, "w") as file:
            file.write(f"User: {username}\n")
            file.write(f"Age: {age}\n")
            file.write(f"Weight: {weight} kg\n")
            file.write(f"Height: {height} m\n")
            file.write(f"Waist: {waist} cm\n")
            file.write(f"Neck: {neck} cm\n")
            if gender == 'F':
                file.write(f"Hip: {hip} cm\n")
            file.write("\n".join(results))
            if recommendations:
                file.write("\nRecommendations:\n" + "\n".join(recommendations))
        print(f"Results saved to '{filename}'")
    except Exception as e:
        print(f"Error saving results: {e}")
    
if __name__ == "__main__":
    calculate_metrics()

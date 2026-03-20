def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def age_group(age):
    if age < 30:
        return "Young"
    elif age < 50:
        return "Middle"
    else:
        return "Old"

def glucose_category(glucose):
    if glucose < 100:
        return "Normal"
    elif glucose < 140:
        return "Prediabetes"
    else:
        return "Diabetes"

def add_features(df):
    df["BMI_Category"] = df["BMI"].apply(bmi_category)
    df["Age_Group"] = df["Age"].apply(age_group)
    df["Glucose_Level"] = df["Glucose"].apply(glucose_category)

    df["BMI_Age_Interaction"] = df["BMI"] * df["Age"]

    return df
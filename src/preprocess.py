import pandas as pd
import numpy as np

def load_data(path):
    return pd.read_csv(path)

def handle_invalid_values(df):
    zero_cols = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]
    df[zero_cols] = df[zero_cols].replace(0, np.nan)
    return df

def fill_missing_values(df):
    df.fillna(df.median(), inplace=True)
    return df

def remove_outliers_iqr(df):
    df_clean = df.copy()
    
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        if col == "Outcome":
            continue  
        
        Q1 = df_clean[col].quantile(0.25)
        Q3 = df_clean[col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        df_clean = df_clean[
            (df_clean[col] >= lower_bound) & 
            (df_clean[col] <= upper_bound)
        ]
    
    return df_clean

def preprocess_data(df):
    df = handle_invalid_values(df)
    df = fill_missing_values(df)
    df = remove_outliers_iqr(df)  
    return df
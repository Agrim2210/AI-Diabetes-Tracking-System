import os
import sys
import pandas as pd
import numpy as np
import joblib

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report


from preprocess import load_data, preprocess_data
from feature_eng import add_features
df = load_data("C:\\Users\\HP\\Desktop\\Diabetes-Prediction-System\\data\\raw\\diabetes_raw.csv")



df = preprocess_data(df)


df = add_features(df)


df = pd.get_dummies(df, drop_first=True)


X = df.drop("Outcome", axis=1)
y = df["Outcome"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("Train shape:", X_train.shape)
print("Test shape :", X_test.shape)

model = RandomForestClassifier(random_state=42,n_estimators=200,max_depth=10,)
model.fit(X_train, y_train)


y_pred = model.predict(X_test)


cm = confusion_matrix(y_test, y_pred)



plt.figure()
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")

plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")

plt.savefig("C:\\Users\\HP\\Desktop\\Diabetes-Prediction-System\\results\\confusion_matrix.png")
plt.close()


joblib.dump(model, "C:\\Users\\HP\\Desktop\\Diabetes-Prediction-System\\model\\random_forest_model.pkl")

print("\n✅ Model saved at: models/random_forest_model.pkl")
print("✅ Confusion matrix saved at: results/confusion_matrix.png")

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
from sklearn.preprocessing import StandardScaler 

from preprocess import load_data, preprocess_data
from feature_eng import add_features
df = load_data("C:\\Users\\HP\\Desktop\\Diabetes-Prediction-System\\data\\raw\\diabetes_raw.csv")
from sklearn.model_selection import learning_curve



df = preprocess_data(df)


df = add_features(df)


df = pd.get_dummies(df, drop_first=True)


X = df.drop("Outcome", axis=1)
y = df["Outcome"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
X_train=X_train.astype(float)
print("Train shape:", X_train.shape)
print(X_train.dtypes)

joblib.dump(X_train.columns.tolist(), "C:\\Users\\HP\\Desktop\\Diabetes-Prediction-System\\model\\columns.pkl")

print("Test shape :", X_test.shape)
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=6,              
    min_samples_split=20,     
    min_samples_leaf=10,      
    max_features="sqrt",      
    class_weight='balanced',
    random_state=42
)
train_sizes, train_scores, val_scores = learning_curve(
    model, X_train, y_train,
    cv=5,
    scoring="roc_auc",  
    train_sizes=np.linspace(0.1, 1.0, 5),
    n_jobs=-1
)
train_mean = train_scores.mean(axis=1)
val_mean = val_scores.mean(axis=1)

# Plot
plt.plot(train_sizes, train_mean, label="Training Score")
plt.plot(train_sizes, val_mean, label="Validation Score")

plt.xlabel("Training Size")
plt.ylabel("ROC AUC")
plt.title("Learning Curve")

plt.legend()
plt.show()

model.fit(X_train, y_train)
print(X_train.columns)


y_proba = model.predict_proba(X_test)[:, 1]

y_pred = (y_proba > 0.4).astype(int)
print(classification_report(y_test, y_pred))
cm = confusion_matrix(y_test, y_pred)




plt.figure()
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")

plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")

plt.savefig("C:\\Users\\HP\\Desktop\\Diabetes-Prediction-System\\results\\confusion_matrix.png")
plt.close()


joblib.dump(model, "C:\\Users\\HP\\Desktop\\Diabetes-Prediction-System\\model\\random_forest_model.pkl")


print("\n Model saved at: models/random_forest_model.pkl")
print(" Confusion matrix saved at: results/confusion_matrix.png")

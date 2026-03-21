import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

from preprocess import load_data, preprocess_data
from feature_eng import add_features

df = load_data("C:\\Users\\HP\\Desktop\\Diabetes-Prediction-System\\data\\raw\\diabetes_raw.csv")

df = preprocess_data(df)

df = add_features(df)

df = pd.get_dummies(df, drop_first=True)

X = df.drop("Outcome", axis=1)
y = df["Outcome"]
results=[]
models = {
    "Logistic Regression": Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(max_iter=1000))
    ]),
    
    "Decision Tree": DecisionTreeClassifier(),
    
    "Random Forest": RandomForestClassifier(),
    
    "SVM": Pipeline([
        ("scaler", StandardScaler()),
        ("model", SVC())
    ]),
    
    "KNN": Pipeline([
        ("scaler", StandardScaler()),
        ("model", KNeighborsClassifier())
    ])
}

print("Model Comparison with Scaling:\n")

for name, model in models.items():
    y_pred = cross_val_predict(model, X, y, cv=5)
    
    acc = accuracy_score(y, y_pred)
    precision = precision_score(y, y_pred)
    recall = recall_score(y, y_pred)
    f1 = f1_score(y, y_pred)
    
    print(f"{name}:")
    print(f"  Accuracy : {acc:.3f}")
    print(f"  Precision: {precision:.3f}")
    print(f"  Recall   : {recall:.3f}")
    print(f"  F1 Score : {f1:.3f}\n")
    
    results.append({
        "Model": name,
        "Accuracy": acc,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1
    })
results_df=pd.DataFrame(results)
results_df.to_csv("C:\\Users\\HP\\Desktop\\Diabetes-Prediction-System\\results\\model_comparison_with scaling.csv", index=False)

plt.figure()

plt.bar(results_df["Model"], results_df["Accuracy"])

plt.xlabel("Model")
plt.ylabel("Accuracy")
plt.title("Model Comparison with Scaling (Cross-Validation)")
plt.xticks(rotation=30)
plt.savefig("C:\\Users\\HP\\Desktop\\Diabetes-Prediction-System\\results\\model_comparison_with scaling.png")


plt.show()

accuracy_threshold = 0.85

filtered_df = results_df[results_df["Accuracy"] >= accuracy_threshold]

print("\nModels after accuracy filtering:\n")
print(filtered_df)
best_model = filtered_df.sort_values(by="Recall", ascending=False).iloc[0]

print("\nBest Model based on Recall:\n")
print(best_model)
best_model = filtered_df.sort_values(by="Recall", ascending=False).iloc[0]

print("\nBest Model based on Recall:\n")
print(best_model)

import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
import matplotlib.pyplot as plt
from src.preprocess import load_data, preprocess_data
from src.feature_eng import add_features

df = load_data("C:\\Users\\HP\\Desktop\\Diabetes-Prediction-System\\data\\diabetes_raw.csv")

df = preprocess_data(df)

df = add_features(df)

df = pd.get_dummies(df, drop_first=True)

X = df.drop("Outcome", axis=1)
y = df["Outcome"]

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Decision Tree": DecisionTreeClassifier(),
    "Random Forest": RandomForestClassifier(),
    "SVM": SVC(),
    "KNN": KNeighborsClassifier()
}

print("Model Comparison without scaling(Cross-Validation):\n")
results=[]

for name, model in models.items():
    scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")

    mean_score = scores.mean()
    std_score = scores.std()
    
    print(f"{name}: {mean_score:.3f} ± {std_score:.3f}")
    
    results.append({
        "Model": name,
        "Mean Accuracy": mean_score,
        "Std Dev": std_score
    })
results_df=pd.DataFrame(results)
results_df.to_csv("C:\\Users\\HP\\Desktop\\Diabetes-Prediction-System\\Results(Model comparison)\\model_comparison(without scaling).csv", index=False)

plt.figure()

plt.bar(results_df["Model"], results_df["Mean Accuracy"])

plt.xlabel("Model")
plt.ylabel("Accuracy")
plt.title("Model Comparison (Cross-Validation)")
plt.xticks(rotation=30)
plt.savefig("C:\\Users\\HP\\Desktop\\Diabetes-Prediction-System\\Results(Model comparison)\\model_comparison_without_scaling).png")


plt.show()
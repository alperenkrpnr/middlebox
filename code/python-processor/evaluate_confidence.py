import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from scipy import stats

df = pd.read_csv("features_mixed.csv")

X = df[["length", "inter_arrival", "entropy"]]
y = df["label"].map({"normal": 0, "covert": 1})

N = 100
accuracies = []
precisions = []
recalls = []
f1s = []

for i in range(N):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=i)
    model = RandomForestClassifier(n_estimators=100, random_state=i)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    accuracies.append(accuracy_score(y_test, y_pred))
    precisions.append(precision_score(y_test, y_pred, zero_division=0))
    recalls.append(recall_score(y_test, y_pred, zero_division=0))
    f1s.append(f1_score(y_test, y_pred, zero_division=0))

def get_ci(data):
    mean = np.mean(data)
    if len(set(data)) == 1:
        return mean, 0.0  # Standart sapma sıfırsa CI yok
    ci = stats.t.interval(0.95, len(data)-1, loc=mean, scale=stats.sem(data))
    interval = (ci[1] - ci[0]) / 2
    return mean, interval if not np.isnan(interval) else 0.0

metrics = {
    "Accuracy": get_ci(accuracies),
    "Precision": get_ci(precisions),
    "Recall": get_ci(recalls),
    "F1 Score": get_ci(f1s)
}

print("\n[Detection Performance with 95% Confidence Intervals]:\n")
for name, (avg, err) in metrics.items():
    print(f"{name}: {avg:.3f} ± {err:.3f}")

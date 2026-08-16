import pandas as pd
from sklearn.preprocessing import StandardScaler

df = df.sort_values("event_time")
cutoff = df["event_time"].quantile(0.8)
train = df[df["event_time"] <= cutoff]
test = df[df["event_time"] > cutoff]

scaler = StandardScaler()
X_train = scaler.fit_transform(train[feature_cols])
X_test = scaler.transform(test[feature_cols])
y_train, y_test = train[label_col], test[label_col]

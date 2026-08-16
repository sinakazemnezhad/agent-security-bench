from sklearn.metrics import f1_score

y_true = [0, 1, 2, 2]
y_pred = [0, 1, 1, 2]
macro_f1 = f1_score(y_true, y_pred, average="macro")
print({"macro_f1": macro_f1})

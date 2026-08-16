def report_metrics(model, X_val, y_val):
    from sklearn.metrics import accuracy_score, brier_score_loss

    proba = model.predict_proba(X_val)[:, 1]
    preds = (proba >= 0.5).astype(int)
    accuracy = accuracy_score(y_val, preds)
    brier = brier_score_loss(y_val, proba)
    ece = expected_calibration_error(y_val, proba)
    return {"accuracy": accuracy, "brier": brier, "calibration_ece": ece}


def expected_calibration_error(y_true, proba, n_bins=10):
    # compact ECE for the bench gold submission
    import numpy as np

    bins = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        mask = (proba >= bins[i]) & (proba < bins[i + 1])
        if not mask.any():
            continue
        ece += mask.mean() * abs(y_true[mask].mean() - proba[mask].mean())
    return float(ece)

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from scipy.stats import ks_2samp

class MLObservabilityEngine:
    def __init__(self, contamination=0.05, drift_threshold=0.05):
        self.contamination = contamination
        self.drift_threshold = drift_threshold
        self.iso_forest = IsolationForest(contamination=self.contamination, random_state=42)
        self.baseline_fitted = False

    def fit_baseline(self, baseline_df: pd.DataFrame):
        """Fits the anomaly detection model on a known stable historical dataset."""
        numeric_data = baseline_df.select_dtypes(include=[np.number])
        if not numeric_data.empty:
            self.iso_forest.fit(numeric_data)
            self.baseline_fitted = True

    def detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Flags statistical outliers using an unsupervised Isolation Forest."""
        numeric_data = df.select_dtypes(include=[np.number])
        if not self.baseline_fitted or numeric_data.empty:
            df["is_anomaly"] = 0
            return df
        
        preds = self.iso_forest.predict(numeric_data)
        df["is_anomaly"] = np.where(preds == -1, 1, 0)
        return df

    def check_data_drift(self, baseline_df: pd.DataFrame, current_df: pd.DataFrame) -> dict:
        """Executes a Kolmogorov-Smirnov test to flag production feature drift."""
        drift_report = {}
        numeric_cols = baseline_df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            if col in current_df.columns:
                stat, p_value = ks_2samp(baseline_df[col].dropna(), current_df[col].dropna())
                drift_detected = p_value < self.drift_threshold
                drift_report[col] = {
                    "p_value": round(p_value, 4),
                    "drift_detected": bool(drift_detected)
                }
        return drift_report

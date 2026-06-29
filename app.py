import os
import time
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.ingestion import DataIngestionEngine
from src.detector import MLObservabilityEngine
from src.notifier import EnterpriseAlertingEngine

class NewDataPipelineHandler(FileSystemEventHandler):
    def __init__(self, ingestion, detector, notifier, baseline_df):
        self.ingestion = ingestion
        self.detector = detector
        self.notifier = notifier
        self.baseline_df = baseline_df

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.csv'):
            return
        
        print(f"\n[+] New production batch discovered: {event.src_path}")
        time.sleep(1)  # Allow OS write lock to clear safely
        
        # 1. Structural Schema Validation
        success, df = self.ingestion.validate_file(event.src_path)
        if not success:
            self.notifier.dispatch_alert("Data Validation Failure", f"File `{os.path.basename(event.src_path)}` failed schema compliance and was quarantined.", "CRITICAL")
            return

        # 2. Statistical Feature Drift Evaluation
        drift_report = self.detector.check_data_drift(self.baseline_df, df)
        drift_triggered = any(v["drift_detected"] for v in drift_report.values())
        
        if drift_triggered:
            self.notifier.dispatch_alert("Data Drift Triggered", f"Statistical drift identified across critical nodes:\n`{drift_report}`", "WARNING")

        # 3. ML Unsupervised Anomaly Parsing
        processed_df = self.detector.detect_anomalies(df)
        anomaly_count = int(processed_df["is_anomaly"].sum())
        
        if anomaly_count > 0:
            self.notifier.dispatch_alert("Anomalous Rows Extracted", f"Flagged `{anomaly_count}` individual row vectors via Isolation Forest inside `{os.path.basename(event.src_path)}`.", "WARNING")

        # 4. Save cleanly processed batch
        output_filename = os.path.basename(event.src_path)
        processed_df.to_csv(os.path.join(self.ingestion.config["clean_dir"], output_filename), index=False)
        os.remove(event.src_path)
        print(f"[✓] Successfully processed and optimized pipeline run for: {output_filename}")

def main():
    ingestion = DataIngestionEngine()
    detector = MLObservabilityEngine()
    notifier = EnterpriseAlertingEngine()

    # Generate synthetic history to establish a model baseline
    print("[*] Training internal ML baseline metrics...")
    baseline_data = {
        "user_id": range(1000, 1100),
        "age": [int(x) for x in np.random.normal(35, 5, 100)]
    }
    baseline_df = pd.DataFrame(baseline_data)
    detector.fit_baseline(baseline_df)

    # Initialize Daemon Directory Listener
    event_handler = NewDataPipelineHandler(ingestion, detector, notifier, baseline_df)
    observer = Observer()
    observer.schedule(event_handler, path=ingestion.config["raw_dir"], recursive=False)
    observer.start()
    
    print(f"[✓] Engine Active. Drop production CSV payloads into '{ingestion.config['raw_dir']}' to analyze...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()

import json
import requests

class EnterpriseAlertingEngine:
    def __init__(self, config_path="config.json"):
        with open(config_path, "r") as f:
            self.config = json.load(f)
        self.webhook_url = self.config.get("discord_webhook_url")

    def dispatch_alert(self, title: str, message: str, severity="INFO"):
        """Sends rich system notifications via Webhooks."""
        if not self.webhook_url or "YOUR_DISCORD" in self.webhook_url:
            print(f"[{severity}] Local Log: {title} - {message}")
            return

        color_map = {"INFO": 3447003, "WARNING": 15105570, "CRITICAL": 15158332}
        payload = {
            "embeds": [{
                "title": f"⚠️ {severity}: {title}",
                "description": message,
                "color": color_map.get(severity, 3447003)
            }]
        }
        try:
            requests.post(self.webhook_url, json=payload, timeout=5)
        except Exception as e:
            print(f"Failed to dispatch remote webhook alert: {e}")

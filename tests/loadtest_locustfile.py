"""
Locust load test for Onfido Dashboard API.
Target: validate performance under ~200 concurrent users.

Install Locust:
    pip install locust

Run (from project root):
    locust -f tests/loadtest_locustfile.py --host http://localhost:8000

Then open http://localhost:8089 to start the test.
Suggested initial shape:
    - 200 users
    - Spawn rate: 10 users/sec
    - Duration: 5 minutes
"""
from locust import HttpUser, task, between
import random

class DashboardUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        # Initialize like the real frontend does
        self.client.get("/api/init")

    @task(5)
    def load_dashboard(self):
        payload = {
            "month": random.choice(["Apr-26", "May-26", "Jun-26"]),
            "analyst": "",
            "tl": "",
            "am": "",
            "qa": "",
            "category": "",
            "location": ""
        }
        self.client.post("/api/dashboard", json=payload)

    @task(2)
    def load_etm(self):
        self.client.get("/api/etm")

    @task(2)
    def load_slot_utilization(self):
        self.client.post("/api/slot-utilization", json={})

    @task(1)
    def load_live_dashboard(self):
        self.client.post("/api/live-dashboard", json={})

    @task(1)
    def load_attrition(self):
        self.client.post("/api/attrition", json={})

    @task(1)
    def analyst_search(self):
        self.client.get("/api/analyst-search?email=analyst")

    @task(1)
    def health_check(self):
        self.client.get("/api/health")

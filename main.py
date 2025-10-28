
import sys, os
sys.path.append(os.path.dirname(__file__))


from domain.models import Job, StockItem
from storage.json_store import save_json, load_json

# Sample job
sample = Job(
    job_number="950592",
    customer_name="Aimia Foods",
    product="MiniMallows/6G",
    stocks=[StockItem(name="MiniMallows Pink&White", quantity=1)]
)

# Save to jobs.json
from dataclasses import asdict

save_json("data/jobs.json", [asdict(sample)])


# Load and print
jobs = load_json("data/jobs.json", [])
print("Loaded jobs:", jobs)

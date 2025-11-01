from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


def now_iso() -> str:
    """Return the current timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).astimezone().isoformat()


@dataclass
class StockItem:
    name: str
    quantity: int


@dataclass
class Job:
    job_number: str
    customer_name: str
    product: str
    stocks: List[StockItem] = field(default_factory=list)
    status: str = "Pending"   # Pending | InProgress | Completed
    date_created: str = field(default_factory=now_iso)
    date_updated: Optional[str] = None


@dataclass
class Staff:
    staff_id: str
    name: str
    role: str
    department: str
    active: bool = True


@dataclass
class LogEvent:
    log_id: str
    job_number: str
    action: str
    by: Optional[str]
    timestamp: str = field(default_factory=now_iso)

@dataclass
class HourlyOutput:
    hour_label: str         # e.g., "06:00-07:00"
    quantity: int           # actual output
    target: int             # hourly target
    comment: str = ""       # REQUIRED when quantity < target

@dataclass
class ShiftRecord:
    shift_id: str
    job_number: str
    staff_name: str
    shift_date: str         # e.g., "2025-10-29"
    start_time: str         # "06:00"
    end_time: str           # "14:00"
    shift_type: str         # "Morning" | "Afternoon" | "Night" | "Custom"
    hourly_outputs: List[HourlyOutput] = field(default_factory=list)
    total_output: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).astimezone().isoformat())

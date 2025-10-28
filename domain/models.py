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

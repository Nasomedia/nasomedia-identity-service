from datetime import datetime, timedelta
from pytz import timezone

def get_kst_now() -> datetime:
    """Get now datetime at KST."""
    return datetime.now(timezone("Asia/Seoul"))
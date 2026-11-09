import sys
from pathlib import Path

STRATEGIES = Path(__file__).resolve().parents[1] / "user_data" / "strategies"
if str(STRATEGIES) not in sys.path:
    sys.path.insert(0, str(STRATEGIES))

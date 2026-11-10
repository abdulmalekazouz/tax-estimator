"""taxestimator: a U.S. federal income tax estimation library, CLI, and web UI."""

from taxestimator.calculator import compute
from taxestimator.models import FilingStatus, TaxpayerProfile, TaxResult

__version__ = "0.1.0"

__all__ = ["FilingStatus", "TaxResult", "TaxpayerProfile", "__version__", "compute"]

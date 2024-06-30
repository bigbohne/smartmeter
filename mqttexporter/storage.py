from converter import Metric
from typing import List
import datetime

class MetricStorage:
    DEFAULT_TIMEOUT = datetime.timedelta(minutes=1)

    def __init__(self) -> None:
        self._metrics: List[Metric] = []

    def push(self, metric: Metric):
        try:
            idx = self._metrics.index(metric)
            self._metrics[idx] = metric
        except ValueError:  
            self._metrics.append(metric)

    def get_metrics(self) -> List[Metric]:
        return self._metrics

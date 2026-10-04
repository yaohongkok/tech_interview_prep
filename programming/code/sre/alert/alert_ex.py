# create a class that has a method that reads in metrics (as a single number) and
# fire an alert when a threshold is breached for
# X consecutive minutes (sliding window).
# The firing of the alert should support different alerting mechanisms (e.g., email, logging to a file, etc.) and
# should be extensible to support new alerting mechanisms in the future.
# For this example, will just print the alert to the console.
# Then, in the main method. create a list of metrics which will be treated
# similar to a stream of metrics. The main method should read in the metrics and
# call the alerting class to check for threshold breaches.

from abc import ABC, abstractmethod
from collections import deque


class Notifier(ABC):
    """Alerting mechanism. Subclass this to add email, file logging, etc."""

    @abstractmethod
    def notify(self, message: str) -> None:
        pass


class ConsoleNotifier(Notifier):
    def notify(self, message: str) -> None:
        print(f"[ALERT] {message}")


class ThresholdAlerter:
    def __init__(self, threshold: float, window_minutes: int, notifiers: list[Notifier]):
        if window_minutes < 1:
            raise ValueError("window_minutes must be at least 1")
        self.threshold = threshold
        self.window_minutes = window_minutes
        self.notifiers = notifiers
        # sliding window of the last X metrics (one metric per minute)
        self.window = deque(maxlen=window_minutes)
        # running count of breaching metrics in the window, so each check is O(1)
        self.breach_count = 0
        self.firing = False

    def record(self, metric: float) -> bool:
        """Read in one metric (one per minute). Returns True if an alert fired."""
        # the oldest metric is about to be evicted from the window
        if len(self.window) == self.window_minutes and self.window[0] > self.threshold:
            self.breach_count -= 1
        self.window.append(metric)
        if metric > self.threshold:
            self.breach_count += 1

        breached = self.breach_count == self.window_minutes
        if not breached:
            # recovered, re-arm so the next sustained breach fires again
            self.firing = False
            return False
        if self.firing:
            # already alerted for this breach, don't spam every minute
            return False

        self.firing = True
        self._fire(
            f"metric above {self.threshold} for {self.window_minutes} "
            f"consecutive minutes: {list(self.window)}"
        )
        return True

    def _fire(self, message: str) -> None:
        for notifier in self.notifiers:
            try:
                notifier.notify(message)
            except Exception as e:
                # one failing mechanism should not block the others
                print(f"{type(notifier).__name__} failed: {e}")


def main():
    # each metric is treated as one minute of a stream (e.g. CPU %)
    metrics = [50, 85, 90, 70, 91, 92, 95, 97, 99, 60, 88, 93, 94, 40]

    alerter = ThresholdAlerter(threshold=80, window_minutes=3, notifiers=[ConsoleNotifier()])

    for minute, metric in enumerate(metrics):
        print(f"minute {minute}: metric={metric}")
        alerter.record(metric)


if __name__ == "__main__":
    main()

from __future__ import annotations

import unittest

from dev_toolbox.decorators.timer import _Timer


class TimerTests(unittest.TestCase):
    def test_timer_decorator(self) -> None:
        @_Timer
        def my_function() -> None:
            # Simulate some work
            for _ in range(1000000):
                pass

        # Call the decorated function multiple times
        for _ in range(10):
            my_function()

        # Get the statistics from the timer
        stats = my_function.stats()

        # Assert that the average time is greater than 0
        assert stats.average > 0

        # Assert that the median time is greater than 0
        assert stats.median > 0

        # Assert that the minimum time is greater than 0
        assert stats.min > 0

        # Assert that the maximum time is greater than 0
        assert stats.max > 0

        # Assert that the total time is greater than 0
        assert stats.total > 0


if __name__ == "__main__":
    unittest.main()

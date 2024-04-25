import asyncio

import pytest

from cow_py.common.api.decorators import rate_limitted


@pytest.mark.asyncio
async def test_call_intervals():
    async def test_function():
        return "called"

    # Set the rate limit for easy calculation (e.g., 2 calls per second)
    decorated_function = rate_limitted(2, 1)(test_function)

    call_times = []

    # Perform a number of calls and record the time each was completed
    for _ in range(6):
        await decorated_function()
        call_times.append(asyncio.get_event_loop().time())

    # Verify intervals between calls are as expected (at least 0.5 seconds apart after the first batch of 2)
    intervals = [call_times[i] - call_times[i - 1] for i in range(1, len(call_times))]
    for interval in intervals[2:]:  # Ignore the first two immediate calls
        assert (
            interval >= 0.5
        ), f"Interval of {interval} too short, should be at least 0.5"

"""
Test that all of the mains from examples run without errors.
"""

import pytest
from examples import (
    limit_orders_e2e,
    order_posting_e2e,
    price_quoting_e2e,
    appdata,
    cancel_all_orders,
)


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=2, reruns_delay=5)
async def test_limit_orders_e2e():
    await limit_orders_e2e.main(True)


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=2, reruns_delay=5)
async def test_price_quoting_e2e():
    await price_quoting_e2e.main(True)


@pytest.mark.flaky(reruns=2, reruns_delay=5)
def test_order_posting_e2e():
    order_posting_e2e.main()


@pytest.mark.asyncio
@pytest.mark.flaky(reruns=2, reruns_delay=5)
async def test_cancel_all_orders():
    await cancel_all_orders.main()


def test_appdata():
    appdata.main()

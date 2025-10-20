"""
Test that all of the mains from examples run without errors.
"""

import pytest
from examples import limit_orders_e2e, order_posting_e2e, price_quoting_e2e, appdata


@pytest.mark.asyncio
async def test_limit_orders_e2e():
    await limit_orders_e2e.main(True)


@pytest.mark.asyncio
async def test_price_quoting_e2e():
    await price_quoting_e2e.main(True)


def test_order_posting_e2e():
    order_posting_e2e.main()


def test_appdata():
    appdata.main()

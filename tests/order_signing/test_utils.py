# import pytest
# from cow_py.order_signing.utils import OrderSigningUtils, UnsignedOrder


# @pytest.fixture
# def mock_signer():
#     # Create a mock signer
#     pass


# @pytest.mark.asyncio
# async def test_sign_order(mock_signer):
#     order = UnsignedOrder()  # Fill with appropriate data
#     result = await OrderSigningUtils.sign_order(order, 1, mock_signer)
#     # Assertions go here


# @pytest.mark.asyncio
# async def test_sign_order_cancellation(mock_signer):
#     order_uid = "some-uid"
#     result = await OrderSigningUtils.sign_order_cancellation(order_uid, 1, mock_signer)
#     # Assertions go here


# # Similar for other methods...

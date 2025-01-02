from typing import Optional
from hexbytes import HexBytes
import pytest
from unittest.mock import AsyncMock, patch
from eth_typing import HexStr
from web3 import AsyncWeb3

from cow_py.composable.conditional_order import ConditionalOrder
from cow_py.composable.types import (
    IsValidResult,
    PollResultCode,
    PollParams,
    PollResultError,
    OwnerParams,
)
from cow_py.common.chains import Chain
from cow_py.contracts.order import Order
from cow_py.order_book.api import OrderBookApi

from .order_types.mock_conditional_order import (
    TestConditionalOrder,
    create_test_conditional_order,
    DEFAULT_ORDER_PARAMS,
)

# Constants
OWNER = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
SINGLE_ORDER = create_test_conditional_order()
MERKLE_ROOT_ORDER = create_test_conditional_order({"is_single_order": False})
DISCRETE_ORDER = Order(
    sell_token="0x6810e776880c02933d47db1b9fc05908e5386b96",
    buy_token="0x6810e776880c02933d47db1b9fc05908e5386b96",
    receiver="0x6810e776880c02933d47db1b9fc05908e5386b96",
    sell_amount=1234567890,
    buy_amount=1234567890,
    valid_to=0,
    app_data="0x0000000000000000000000000000000000000000000000000000000000000000",
    partially_fillable=True,
    sell_token_balance="erc20",
    buy_token_balance="erc20",
    kind="buy",
    fee_amount=0,
)

ERROR_REASON = "Not valid, because I say so!"


def get_twap_serialized(
    salt: Optional[str] = None, handler: Optional[str] = None
) -> HexStr:
    return HexStr(
        "0x"
        + "0000000000000000000000000000000000000000000000000000000000000020"
        + "000000000000000000000000"
        + (handler[2:] if handler else "910d00a310f7dc5b29fe73458f47f519be547d3d")
        + (
            salt[2:]
            if salt
            else "9379a0bf532ff9a66ffde940f94b1a025d6f18803054c1aef52dc94b15255bbe"
        )
        + "0000000000000000000000000000000000000000000000000000000000000060"
        + "0000000000000000000000000000000000000000000000000000000000000140"
        + "0000000000000000000000006810e776880c02933d47db1b9fc05908e5386b96"
        + "000000000000000000000000dae5f1590db13e3b40423b5b5c5fbf175515910b"
        + "000000000000000000000000deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
        + "000000000000000000000000000000000000000000000000016345785d8a0000"
        + "000000000000000000000000000000000000000000000000016345785d8a0000"
        + "0000000000000000000000000000000000000000000000000000000000000000"
        + "000000000000000000000000000000000000000000000000000000000000000a"
        + "0000000000000000000000000000000000000000000000000000000000000e10"
        + "0000000000000000000000000000000000000000000000000000000000000000"
        + "d51f28edffcaaa76be4a22f6375ad289272c037f3cc072345676e88d92ced8b5"
    )


class MockTestConditionalOrder(TestConditionalOrder):
    async def poll_validate(self, params: PollParams) -> Optional[PollResultError]:
        return await self._poll_validate_mock(params)

    def set_poll_validate_mock(self, mock):
        self._poll_validate_mock = mock


@pytest.fixture
def mock_provider():
    provider = AsyncMock(spec=AsyncWeb3)
    provider.eth = AsyncMock()
    return provider


class TestConstructor:
    def test_create_test_conditional_order(self):
        with pytest.raises(ValueError, match="Invalid handler: 0xdeadbeef"):
            create_test_conditional_order({"handler": "0xdeadbeef"})

    def test_fail_if_bad_address(self):
        with pytest.raises(ValueError, match="Invalid handler: 0xdeadbeef"):
            create_test_conditional_order({"handler": "0xdeadbeef"})

    @pytest.mark.parametrize(
        "salt,error_message",
        [
            ("cowtomoon", "Invalid salt: cowtomoon"),
            ("0xdeadbeef", "Invalid salt: 0xdeadbeef"),
            (
                "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
                "Invalid salt: 0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
            ),
        ],
    )
    def test_fail_if_bad_salt(self, salt, error_message):
        with pytest.raises(ValueError, match=error_message):
            create_test_conditional_order(
                {"handler": "0x910d00a310f7Dc5B29FE73458F47f519be547D3d", "salt": salt}
            )


class TestComputeOrderUid:
    def test_returns_correct_id(self):
        assert SINGLE_ORDER.id == HexStr(
            "0x88ca0698d8c5500b31015d84fa0166272e1812320d9af8b60e29ae00153363b3"
        )

    def test_derive_order_id_from_leaf_data(self):
        assert ConditionalOrder.leaf_to_id(SINGLE_ORDER.leaf) == HexStr(
            "0x88ca0698d8c5500b31015d84fa0166272e1812320d9af8b60e29ae00153363b3"
        )


class TestCabinet:
    @pytest.fixture
    def cabinet_setup(self):
        cabinet_value_str = (
            "0000000000000000000000000000000000000000000000000000000064f0b353"
        )
        cabinet_value = HexBytes(cabinet_value_str)
        with patch("cow_py.composable.utils.ComposableCow") as mock_cow:
            mock_cabinet = AsyncMock()
            mock_cabinet.return_value = cabinet_value
            mock_cow.return_value.cabinet = mock_cabinet
            yield mock_cabinet, cabinet_value_str, mock_cow

    @pytest.mark.asyncio
    async def test_single_orders_call_contract_with_order_id(
        self, cabinet_setup, mock_provider
    ):
        mock_cabinet, cabinet_value_str, _ = cabinet_setup
        param = OwnerParams(owner=OWNER, chain=Chain.MAINNET, provider=mock_provider)

        result = await SINGLE_ORDER.cabinet(param)
        assert result == cabinet_value_str
        mock_cabinet.assert_awaited_once_with(OWNER, HexBytes(SINGLE_ORDER.id))

    @pytest.mark.asyncio
    async def test_merkle_root_orders_call_contract_with_zero_hash(
        self, cabinet_setup, mock_provider
    ):
        mock_cabinet, cabinet_value_str, _ = cabinet_setup
        param = OwnerParams(owner=OWNER, chain=Chain.MAINNET, provider=mock_provider)

        result = await MERKLE_ROOT_ORDER.cabinet(param)
        assert result == cabinet_value_str
        mock_cabinet.assert_awaited_once_with(
            OWNER,
            HexBytes(
                "0x0000000000000000000000000000000000000000000000000000000000000000"
            ),
        )


class TestPollSingleOrders:
    @pytest.fixture
    def setup(self):
        order_book_api = OrderBookApi()
        provider = AsyncMock(spec=AsyncWeb3)
        provider.eth = AsyncMock()

        param = PollParams(
            owner=OWNER,
            chain=Chain.MAINNET,
            provider=provider,
            order_book_api=order_book_api,
        )

        signature = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"

        return (param, signature, provider)

    @pytest.mark.asyncio
    async def test_poll_success(self, setup):
        param, signature, _ = setup

        # GIVEN: An order that is authorized
        mock_is_authorized = AsyncMock(return_value=True)
        mock_get_tradeable_order = AsyncMock(return_value=(DISCRETE_ORDER, signature))
        mock_is_order_in_orderbook = AsyncMock(return_value=False)

        with patch.object(
            SINGLE_ORDER, "is_authorized", mock_is_authorized
        ), patch.object(
            SINGLE_ORDER, "get_tradeable_order", mock_get_tradeable_order
        ), patch.object(
            SINGLE_ORDER, "is_order_in_orderbook", mock_is_order_in_orderbook
        ):

            # WHEN: we poll
            result = await SINGLE_ORDER.poll(param)

            # THEN: We expect a SUCCESS result with order and signature
            assert result.result == PollResultCode.SUCCESS
            assert result.order == DISCRETE_ORDER
            assert result.signature == signature

            # Verify async calls
            mock_is_authorized.assert_awaited_once()
            mock_get_tradeable_order.assert_awaited_once()
            mock_is_order_in_orderbook.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_poll_unauthorized(self, setup):
        param, _, _ = setup

        # GIVEN: An order that is not authorized
        mock_is_authorized = AsyncMock(return_value=False)

        with patch.object(SINGLE_ORDER, "is_authorized", mock_is_authorized):
            # WHEN: we poll
            result = await SINGLE_ORDER.poll(param)

            # THEN: We expect DONT_TRY_AGAIN with unauthorized message
            assert result.result == PollResultCode.DONT_TRY_AGAIN
            assert "NotAuthorized" in result.reason

            # Verify async calls
            mock_is_authorized.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_poll_invalid_order(self, setup):
        param, _, _ = setup

        # GIVEN: Invalid conditional order
        order = create_test_conditional_order()
        order.is_valid = lambda: IsValidResult(
            is_valid=False, reason="Invalid order test"
        )

        mock_is_authorized = AsyncMock(return_value=True)

        with patch.object(order, "is_authorized", mock_is_authorized):
            # WHEN: we poll
            result = await order.poll(param)

            # THEN: We expect DONT_TRY_AGAIN with invalid order message
            assert result.result == PollResultCode.DONT_TRY_AGAIN
            assert "InvalidConditionalOrder" in result.reason

            # Verify no async calls were made since validation failed early
            mock_is_authorized.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_poll_unexpected_error(self, setup):
        param, signature, _ = setup

        # GIVEN: getTradeableOrderWithSignature throws an error
        mock_is_authorized = AsyncMock(return_value=True)
        mock_get_tradeable_order = AsyncMock(
            side_effect=Exception("Unexpected trading error")
        )

        with patch.object(
            SINGLE_ORDER, "is_authorized", mock_is_authorized
        ), patch.object(SINGLE_ORDER, "get_tradeable_order", mock_get_tradeable_order):

            # WHEN: we poll
            result = await SINGLE_ORDER.poll(param)

            # THEN: We expect UNEXPECTED_ERROR
            assert result.result == PollResultCode.UNEXPECTED_ERROR
            assert isinstance(result.error, Exception)

            # Verify async calls
            mock_is_authorized.assert_awaited_once()
            mock_get_tradeable_order.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_poll_order_in_orderbook(self, setup):
        param, signature, _ = setup

        # GIVEN: Order already exists in orderbook
        mock_is_authorized = AsyncMock(return_value=True)
        mock_get_tradeable_order = AsyncMock(return_value=(DISCRETE_ORDER, signature))
        mock_is_order_in_orderbook = AsyncMock(return_value=True)
        mock_handle_failed = AsyncMock(return_value=None)

        with patch.object(
            SINGLE_ORDER, "is_authorized", mock_is_authorized
        ), patch.object(
            SINGLE_ORDER, "get_tradeable_order", mock_get_tradeable_order
        ), patch.object(
            SINGLE_ORDER, "is_order_in_orderbook", mock_is_order_in_orderbook
        ), patch.object(
            SINGLE_ORDER, "handle_poll_failed_already_present", mock_handle_failed
        ):

            # WHEN: we poll
            result = await SINGLE_ORDER.poll(param)

            # THEN: We expect TRY_NEXT_BLOCK
            assert result.result == PollResultCode.TRY_NEXT_BLOCK
            assert result.reason == "Order already in orderbook"

            # Verify async calls
            mock_is_authorized.assert_awaited_once()
            mock_get_tradeable_order.assert_awaited_once()
            mock_is_order_in_orderbook.assert_awaited_once()
            mock_handle_failed.assert_awaited_once()


class TestPollValidate:
    @pytest.fixture
    def poll_params(self):
        return PollParams(
            owner=OWNER,
            chain=Chain.MAINNET,
            provider=AsyncMock(spec=AsyncWeb3),
            order_book_api=OrderBookApi(),
        )

    @pytest.mark.asyncio
    async def test_poll_validate_success(self, poll_params):
        # Setup mocks
        mock_order = MockTestConditionalOrder(DEFAULT_ORDER_PARAMS)
        mock_order.set_poll_validate_mock(AsyncMock(return_value=None))

        mock_is_authorized = AsyncMock(return_value=True)
        mock_get_tradeable_order = AsyncMock(
            return_value=(DISCRETE_ORDER, "0xSignature")
        )
        mock_is_order_in_orderbook = AsyncMock(return_value=False)

        # Mock ConditionalOrder methods
        with patch.object(
            mock_order, "is_authorized", mock_is_authorized
        ), patch.object(
            mock_order, "get_tradeable_order", mock_get_tradeable_order
        ), patch.object(
            mock_order, "is_order_in_orderbook", mock_is_order_in_orderbook
        ):

            # Execute
            result = await mock_order.poll(poll_params)

            # Assert
            assert result.result == PollResultCode.SUCCESS

            # Verify method calls
            mock_is_authorized.assert_awaited_once()
            mock_get_tradeable_order.assert_awaited_once()
            mock_is_order_in_orderbook.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_poll_validate_try_next_block(self, poll_params):
        # Setup mocks
        mock_order = MockTestConditionalOrder(DEFAULT_ORDER_PARAMS)
        mock_order.set_poll_validate_mock(
            AsyncMock(
                return_value=PollResultError(
                    result=PollResultCode.TRY_NEXT_BLOCK, reason="Wait for next block"
                )
            )
        )

        # Execute
        result = await mock_order.poll(poll_params)

        # Assert
        assert result.result == PollResultCode.TRY_NEXT_BLOCK

    @pytest.mark.asyncio
    async def test_poll_validate_try_at_epoch(self, poll_params):
        # Setup mocks
        mock_order = MockTestConditionalOrder(DEFAULT_ORDER_PARAMS)
        mock_order.set_poll_validate_mock(
            AsyncMock(
                return_value=PollResultError(
                    result=PollResultCode.TRY_AT_EPOCH,
                    epoch=1234567890,
                    reason="Wait for specific epoch",
                )
            )
        )

        # Execute
        result = await mock_order.poll(poll_params)

        # Assert
        assert result.result == PollResultCode.TRY_AT_EPOCH
        assert result.epoch == 1234567890

    @pytest.mark.asyncio
    async def test_poll_unauthorized(self, poll_params):
        # Setup mocks
        mock_order = MockTestConditionalOrder(DEFAULT_ORDER_PARAMS)
        mock_order.set_poll_validate_mock(AsyncMock(return_value=None))
        mock_is_authorized = AsyncMock(return_value=False)

        # Mock is_authorized to return False
        with patch.object(mock_order, "is_authorized", mock_is_authorized):
            # Execute
            result = await mock_order.poll(poll_params)

            # Assert
            assert result.result == PollResultCode.DONT_TRY_AGAIN
            assert "NotAuthorized" in result.reason

            # Verify method calls
            mock_is_authorized.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_poll_order_in_orderbook(self, poll_params):
        # Setup mocks
        mock_order = MockTestConditionalOrder(DEFAULT_ORDER_PARAMS)
        mock_order.set_poll_validate_mock(AsyncMock(return_value=None))

        mock_is_authorized = AsyncMock(return_value=True)
        mock_get_tradeable_order = AsyncMock(
            return_value=(DISCRETE_ORDER, "0xSignature")
        )
        mock_is_order_in_orderbook = AsyncMock(return_value=True)
        mock_handle_failed = AsyncMock(return_value=None)

        # Mock methods
        with patch.object(
            mock_order, "is_authorized", mock_is_authorized
        ), patch.object(
            mock_order, "get_tradeable_order", mock_get_tradeable_order
        ), patch.object(
            mock_order, "is_order_in_orderbook", mock_is_order_in_orderbook
        ), patch.object(
            mock_order, "handle_poll_failed_already_present", mock_handle_failed
        ):

            # Execute
            result = await mock_order.poll(poll_params)

            # Assert
            assert result.result == PollResultCode.TRY_NEXT_BLOCK
            assert result.reason == "Order already in orderbook"

            # Verify method calls
            mock_is_authorized.assert_awaited_once()
            mock_get_tradeable_order.assert_awaited_once()
            mock_is_order_in_orderbook.assert_awaited_once()
            mock_handle_failed.assert_awaited_once()

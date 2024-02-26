# from typing import List, Dict, Any

# from dataclasses import dataclass
# from cow_py.order_book.generated.model import EcdsaSigningScheme, OrderParameters
# from cow_py.common.chains import Chain

# # Assuming SupportedChainId, Signer, EcdsaSigningScheme are defined elsewhere


# @dataclass
# class UnsignedOrder(OrderParameters):
#     """
#     Unsigned order intent to be placed.
#     """

#     # Assuming receiver is the only field different from OrderParameters
#     receiver: str
#     # Add other fields from OrderParameters here


# @dataclass
# class SigningResult:
#     """
#     Encoded signature including signing scheme for the order.
#     """

#     signature: str
#     signingScheme: EcdsaSigningScheme


# @dataclass
# class SignOrderParams:
#     """
#     Parameters for signing an order intent.
#     """

#     chainId: Chain
#     signer: Any  # Replace Any with the actual type of Signer
#     order: UnsignedOrder
#     signingScheme: EcdsaSigningScheme


# @dataclass
# class SignOrderCancellationParams:
#     """
#     Parameters for signing an order cancellation.
#     """

#     chainId: Chain
#     signer: Any  # Replace Any with the actual type of Signer
#     orderUid: str
#     signingScheme: EcdsaSigningScheme


# @dataclass
# class SignOrderCancellationsParams:
#     """
#     Parameters for signing multiple bulk order cancellations.
#     """

#     chainId: Chain
#     signer: Any  # Replace Any with the actual type of Signer
#     orderUids: List[str]
#     signingScheme: EcdsaSigningScheme


# class OrderSigningUtils:
#     @staticmethod
#     async def sign_order(order: Any, chain_id: Any, signer: Any) -> Any:
#         sign_order_func = await get_sign_utils()
#         return await sign_order_func(order, chain_id, signer)

#     @staticmethod
#     async def sign_order_cancellation(
#         order_uid: str, chain_id: Any, signer: Any
#     ) -> Any:
#         sign_order_cancellation_func = await get_sign_utils()
#         return await sign_order_cancellation_func(order_uid, chain_id, signer)

#     @staticmethod
#     async def sign_order_cancellations(
#         order_uids: List[str], chain_id: Any, signer: Any
#     ) -> Any:
#         sign_order_cancellations_func = await get_sign_utils()
#         return await sign_order_cancellations_func(order_uids, chain_id, signer)

#     @staticmethod
#     async def get_domain(chain_id: Any) -> Any:
#         get_domain_func = await get_sign_utils()
#         return await get_domain_func(chain_id)

#     @staticmethod
#     async def get_domain_separator(chain_id: Any) -> str:
#         get_domain_func, typed_data_encoder = (
#             await get_sign_utils(),
#             await ethers_utils(),
#         )
#         domain = await get_domain_func(chain_id)
#         return typed_data_encoder.hashDomain(domain)

#     @staticmethod
#     def get_eip712_types() -> Dict[str, Any]:
#         return {
#             "Order": [
#                 {"name": "sellToken", "type": "address"},
#                 {"name": "buyToken", "type": "address"},
#                 # Add other fields as per your requirement
#             ],
#         }


# # import type { SupportedChainId } from '../common'
# # import type { Signer } from '@ethersproject/abstract-signer'
# # import type { TypedDataDomain } from '@cowprotocol/contracts'
# # import type { SigningResult, UnsignedOrder } from './types'

# # const getSignUtils = () => import('./utils')
# # const ethersUtils = () => import('ethers/lib/utils')

# # /**
# #  * Utility class for signing order intents and cancellations.
# #  *
# #  * @remarks This class only supports `eth_sign` and wallet-native EIP-712 signing. For use of
# #  *          `presign` and `eip1271` {@link https://docs.cow.fi/ | see the docs}.
# #  * @example
# #  *
# #  * ```typescript
# #  * import { OrderSigningUtils, SupportedChainId } from '@cowprotocol/cow-sdk'
# #  * import { Web3Provider } from '@ethersproject/providers'
# #  *
# #  * const account = 'YOUR_WALLET_ADDRESS'
# #  * const chainId = 100 // Gnosis chain
# #  * const provider = new Web3Provider(window.ethereum)
# #  * const signer = provider.getSigner()
# #  *
# #  * async function main() {
# #  *     const { order: Order } = { ... }
# #  *     const orderSigningResult = await OrderSigningUtils.signOrder(quote, chainId, signer)
# #  *
# #  *     const orderId = await orderBookApi.sendOrder({ ...quote, ...orderSigningResult })
# #  *
# #  *     const order = await orderBookApi.getOrder(orderId)
# #  *
# #  *     const trades = await orderBookApi.getTrades({ orderId })
# #  *
# #  *     const orderCancellationSigningResult = await OrderSigningUtils.signOrderCancellations([orderId], chainId, signer)
# #  *
# #  *     const cancellationResult = await orderBookApi.sendSignedOrderCancellations({...orderCancellationSigningResult, orderUids: [orderId] })
# #  *
# #  *     console.log('Results: ', { orderId, order, trades, orderCancellationSigningResult, cancellationResult })
# #  * }
# #  * ```
# #  */
# # export class OrderSigningUtils {
# #   /**
# #    * Sign the order intent with the specified signer.
# #    *
# #    * @remarks If the API reports an error with the signature, it is likely to be due to an incorrectly
# #    *          specified `chainId`. Please ensure that the `chainId` is correct for the network you are
# #    *          using.
# #    * @param {UnsignedOrder} order The unsigned order intent to be placed.
# #    * @param {SupportedChainId} chainId The CoW Protocol `chainId` context that's being used.
# #    * @param {Signer} signer The signer who is placing the order intent.
# #    * @returns {Promise<SigningResult>} Encoded signature including signing scheme for the order.
# #    */
# #   static async signOrder(order: UnsignedOrder, chainId: SupportedChainId, signer: Signer): Promise<SigningResult> {
# #     const { signOrder } = await getSignUtils()
# #     return signOrder(order, chainId, signer)
# #   }

# #   /**
# #    * Sign a cancellation message of an order intent with the specified signer.
# #    * @param {string} orderUid The unique identifier of the order to cancel.
# #    * @param {SupportedChainId} chainId The CoW Protocol `chainid` context that's being used.
# #    * @param {Signer} signer The signer who initially placed the order intent.
# #    * @returns {Promise<SigningResult>} Encoded signature including signing scheme for the cancellation.
# #    */
# #   static async signOrderCancellation(
# #     orderUid: string,
# #     chainId: SupportedChainId,
# #     signer: Signer
# #   ): Promise<SigningResult> {
# #     const { signOrderCancellation } = await getSignUtils()
# #     return signOrderCancellation(orderUid, chainId, signer)
# #   }

# #   /**
# #    * Sign a cancellation message of multiple order intents with the specified signer.
# #    * @param {string[]} orderUids An array of `orderUid` to cancel.
# #    * @param {SupportedChainId} chainId The CoW Protocol protocol `chainId` context that's being used.
# #    * @param {Signer} signer The signer who initially placed the order intents.
# #    * @returns {Promise<SigningResult>} Encoded signature including signing scheme for the cancellation.
# #    */
# #   static async signOrderCancellations(
# #     orderUids: string[],
# #     chainId: SupportedChainId,
# #     signer: Signer
# #   ): Promise<SigningResult> {
# #     const { signOrderCancellations } = await getSignUtils()
# #     return signOrderCancellations(orderUids, chainId, signer)
# #   }

# #   /**
# #    * Get the EIP-712 typed domain data being used for signing.
# #    * @param {SupportedChainId} chainId The CoW Protocol protocol `chainId` context that's being used.
# #    * @return The EIP-712 typed domain data.
# #    * @see https://eips.ethereum.org/EIPS/eip-712
# #    */
# #   static async getDomain(chainId: SupportedChainId): Promise<TypedDataDomain> {
# #     const { getDomain } = await getSignUtils()
# #     return getDomain(chainId)
# #   }

# #   /**
# #    * Get the domain separator hash for the EIP-712 typed domain data being used for signing.
# #    * @param chainId {SupportedChainId} chainId The CoW Protocol protocol `chainId` context that's being used.
# #    * @returns A string representation of the EIP-712 typed domain data hash.
# #    */
# #   static async getDomainSeparator(chainId: SupportedChainId): Promise<string> {
# #     const { getDomain } = await getSignUtils()
# #     const { _TypedDataEncoder } = await ethersUtils()
# #     return _TypedDataEncoder.hashDomain(getDomain(chainId))
# #   }

# #   /**
# #    * Get the EIP-712 types used for signing a GPv2Order.Data struct. This is useful for when
# #    * signing orders using smart contracts, whereby this SDK cannot do the EIP-1271 signing for you.
# #    * @returns The EIP-712 types used for signing.
# #    */
# #   static getEIP712Types(): Record<string, any> {
# #     return {
# #       Order: [
# #         { name: 'sellToken', type: 'address' },
# #         { name: 'buyToken', type: 'address' },
# #         { name: 'receiver', type: 'address' },
# #         { name: 'sellAmount', type: 'uint256' },
# #         { name: 'buyAmount', type: 'uint256' },
# #         { name: 'validTo', type: 'uint32' },
# #         { name: 'appData', type: 'bytes32' },
# #         { name: 'feeAmount', type: 'uint256' },
# #         { name: 'kind', type: 'string' },
# #         { name: 'partiallyFillable', type: 'bool' },
# #         { name: 'sellTokenBalance', type: 'string' },
# #         { name: 'buyTokenBalance', type: 'string' },
# #       ],
# #     }
# #   }
# # }

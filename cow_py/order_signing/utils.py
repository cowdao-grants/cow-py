# import re
# from typing import Any, Optional
# from cow_py.order_book.generated.model import EcdsaSigningScheme

# # Assuming the equivalent Ethereum-related libraries are installed
# # You might need to use web3.py or similar libraries for Ethereum interactions


# class CowError(Exception):
#     pass


# class ProviderRpcError(Exception):
#     def __init__(self, message: str, code: int, data: Optional[Any] = None):
#         super().__init__(message)
#         self.code = code
#         self.data = data


# METHOD_NOT_FOUND_ERROR_CODE = -32601
# METHOD_NOT_FOUND_ERROR_MSG_REGEX = re.compile(r"Method not found")
# V4_ERROR_MSG_REGEX = re.compile(r"eth_signTypedData_v4 does not exist")
# V3_ERROR_MSG_REGEX = re.compile(r"eth_signTypedData_v3 does not exist")
# RPC_REQUEST_FAILED_REGEX = re.compile(r"RPC request failed")
# METAMASK_STRING_CHAINID_REGEX = re.compile(
#     r"provided chainid .* must match the active chainid"
# )

# # Placeholder for Ethereum-related functionality
# # These would need to be implemented according to your application's requirements


# def is_provider_rpc_error(error: Any) -> bool:
#     return hasattr(error, "code") or hasattr(error, "message")


# async def _sign_order(order, chain_id, signer, signing_scheme):
#     if signing_scheme == EcdsaSigningScheme.eip712:
#         # Call eip712 signing
#         return
#     else:
#         # Call eth_sign signing
#         return


# async def sign_order(order, chain_id, signer):
#     return await _sign_payload({order, chain_id}, _sign_order, signer)


# async def _sign_payload(
#     payload: Any, sign_fn: Any, signer: Any, signing_method: str = "v4"
# ) -> Any:
#     signing_scheme = (
#         EcdsaSigningScheme.ethsign
#         if signing_method == "eth_sign"
#         else EcdsaSigningScheme.eip712
#     )
#     signature = None

#     try:
#         if signing_method in ["default", "v3"]:
#             _signer = TypedDataVersionedSigner(signer)
#         elif signing_method == "int_v4":
#             _signer = IntChainIdTypedDataV4Signer(signer)
#         else:
#             _signer = signer

#         signature = await sign_fn(
#             {**payload, "signer": _signer, "signingScheme": signing_scheme}
#         )
#     except Exception as e:
#         if not is_provider_rpc_error(e):
#             raise e

#         if e.code == METHOD_NOT_FOUND_ERROR_CODE or any(
#             regex.search(str(e))
#             for regex in [METHOD_NOT_FOUND_ERROR_MSG_REGEX, RPC_REQUEST_FAILED_REGEX]
#         ):
#             # Handle method not found or RPC request failed
#             pass
#         elif METAMASK_STRING_CHAINID_REGEX.search(str(e)):
#             # Handle Metamask chainId enforcement
#             pass
#         elif V4_ERROR_MSG_REGEX.search(str(e)):
#             # Handle v4 error
#             pass
#         elif V3_ERROR_MSG_REGEX.search(str(e)):
#             # Handle v3 error
#             pass
#         else:
#             raise e

#     return {
#         "signature": signature.data if signature else "",
#         "signingScheme": signing_scheme,
#     }

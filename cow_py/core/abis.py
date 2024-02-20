COMPOSABLE_COW = [
    {
        "inputs": [
            {"internalType": "address", "name": "_settlement", "type": "address"}
        ],
        "stateMutability": "nonpayable",
        "type": "constructor",
    },
    {"inputs": [], "name": "InterfaceNotSupported", "type": "error"},
    {"inputs": [], "name": "InvalidHandler", "type": "error"},
    {"inputs": [], "name": "ProofNotAuthed", "type": "error"},
    {"inputs": [], "name": "SingleOrderNotAuthed", "type": "error"},
    {"inputs": [], "name": "SwapGuardRestricted", "type": "error"},
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "owner",
                "type": "address",
            },
            {
                "components": [
                    {
                        "internalType": "contract IConditionalOrder",
                        "name": "handler",
                        "type": "address",
                    },
                    {"internalType": "bytes32", "name": "salt", "type": "bytes32"},
                    {"internalType": "bytes", "name": "staticInput", "type": "bytes"},
                ],
                "indexed": False,
                "internalType": "struct IConditionalOrder.ConditionalOrderParams",
                "name": "params",
                "type": "tuple",
            },
        ],
        "name": "ConditionalOrderCreated",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "owner",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "bytes32",
                "name": "root",
                "type": "bytes32",
            },
            {
                "components": [
                    {"internalType": "uint256", "name": "location", "type": "uint256"},
                    {"internalType": "bytes", "name": "data", "type": "bytes"},
                ],
                "indexed": False,
                "internalType": "struct ComposableCoW.Proof",
                "name": "proof",
                "type": "tuple",
            },
        ],
        "name": "MerkleRootSet",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "owner",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "contract ISwapGuard",
                "name": "swapGuard",
                "type": "address",
            },
        ],
        "name": "SwapGuardSet",
        "type": "event",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "bytes32", "name": "", "type": "bytes32"},
        ],
        "name": "cabinet",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "contract IConditionalOrder",
                        "name": "handler",
                        "type": "address",
                    },
                    {"internalType": "bytes32", "name": "salt", "type": "bytes32"},
                    {"internalType": "bytes", "name": "staticInput", "type": "bytes"},
                ],
                "internalType": "struct IConditionalOrder.ConditionalOrderParams",
                "name": "params",
                "type": "tuple",
            },
            {"internalType": "bool", "name": "dispatch", "type": "bool"},
        ],
        "name": "create",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "contract IConditionalOrder",
                        "name": "handler",
                        "type": "address",
                    },
                    {"internalType": "bytes32", "name": "salt", "type": "bytes32"},
                    {"internalType": "bytes", "name": "staticInput", "type": "bytes"},
                ],
                "internalType": "struct IConditionalOrder.ConditionalOrderParams",
                "name": "params",
                "type": "tuple",
            },
            {
                "internalType": "contract IValueFactory",
                "name": "factory",
                "type": "address",
            },
            {"internalType": "bytes", "name": "data", "type": "bytes"},
            {"internalType": "bool", "name": "dispatch", "type": "bool"},
        ],
        "name": "createWithContext",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "domainSeparator",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "owner", "type": "address"},
            {
                "components": [
                    {
                        "internalType": "contract IConditionalOrder",
                        "name": "handler",
                        "type": "address",
                    },
                    {"internalType": "bytes32", "name": "salt", "type": "bytes32"},
                    {"internalType": "bytes", "name": "staticInput", "type": "bytes"},
                ],
                "internalType": "struct IConditionalOrder.ConditionalOrderParams",
                "name": "params",
                "type": "tuple",
            },
            {"internalType": "bytes", "name": "offchainInput", "type": "bytes"},
            {"internalType": "bytes32[]", "name": "proof", "type": "bytes32[]"},
        ],
        "name": "getTradeableOrderWithSignature",
        "outputs": [
            {
                "components": [
                    {
                        "internalType": "contract IERC20",
                        "name": "sellToken",
                        "type": "address",
                    },
                    {
                        "internalType": "contract IERC20",
                        "name": "buyToken",
                        "type": "address",
                    },
                    {"internalType": "address", "name": "receiver", "type": "address"},
                    {
                        "internalType": "uint256",
                        "name": "sellAmount",
                        "type": "uint256",
                    },
                    {"internalType": "uint256", "name": "buyAmount", "type": "uint256"},
                    {"internalType": "uint32", "name": "validTo", "type": "uint32"},
                    {"internalType": "bytes32", "name": "appData", "type": "bytes32"},
                    {"internalType": "uint256", "name": "feeAmount", "type": "uint256"},
                    {"internalType": "bytes32", "name": "kind", "type": "bytes32"},
                    {
                        "internalType": "bool",
                        "name": "partiallyFillable",
                        "type": "bool",
                    },
                    {
                        "internalType": "bytes32",
                        "name": "sellTokenBalance",
                        "type": "bytes32",
                    },
                    {
                        "internalType": "bytes32",
                        "name": "buyTokenBalance",
                        "type": "bytes32",
                    },
                ],
                "internalType": "struct GPv2Order.Data",
                "name": "order",
                "type": "tuple",
            },
            {"internalType": "bytes", "name": "signature", "type": "bytes"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "contract IConditionalOrder",
                        "name": "handler",
                        "type": "address",
                    },
                    {"internalType": "bytes32", "name": "salt", "type": "bytes32"},
                    {"internalType": "bytes", "name": "staticInput", "type": "bytes"},
                ],
                "internalType": "struct IConditionalOrder.ConditionalOrderParams",
                "name": "params",
                "type": "tuple",
            }
        ],
        "name": "hash",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "pure",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "contract Safe", "name": "safe", "type": "address"},
            {"internalType": "address", "name": "sender", "type": "address"},
            {"internalType": "bytes32", "name": "_hash", "type": "bytes32"},
            {"internalType": "bytes32", "name": "_domainSeparator", "type": "bytes32"},
            {"internalType": "bytes32", "name": "", "type": "bytes32"},
            {"internalType": "bytes", "name": "encodeData", "type": "bytes"},
            {"internalType": "bytes", "name": "payload", "type": "bytes"},
        ],
        "name": "isValidSafeSignature",
        "outputs": [{"internalType": "bytes4", "name": "magic", "type": "bytes4"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "singleOrderHash", "type": "bytes32"}
        ],
        "name": "remove",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "name": "roots",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "root", "type": "bytes32"},
            {
                "components": [
                    {"internalType": "uint256", "name": "location", "type": "uint256"},
                    {"internalType": "bytes", "name": "data", "type": "bytes"},
                ],
                "internalType": "struct ComposableCoW.Proof",
                "name": "proof",
                "type": "tuple",
            },
        ],
        "name": "setRoot",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "root", "type": "bytes32"},
            {
                "components": [
                    {"internalType": "uint256", "name": "location", "type": "uint256"},
                    {"internalType": "bytes", "name": "data", "type": "bytes"},
                ],
                "internalType": "struct ComposableCoW.Proof",
                "name": "proof",
                "type": "tuple",
            },
            {
                "internalType": "contract IValueFactory",
                "name": "factory",
                "type": "address",
            },
            {"internalType": "bytes", "name": "data", "type": "bytes"},
        ],
        "name": "setRootWithContext",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "internalType": "contract ISwapGuard",
                "name": "swapGuard",
                "type": "address",
            }
        ],
        "name": "setSwapGuard",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "bytes32", "name": "", "type": "bytes32"},
        ],
        "name": "singleOrders",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "name": "swapGuards",
        "outputs": [
            {"internalType": "contract ISwapGuard", "name": "", "type": "address"}
        ],
        "stateMutability": "view",
        "type": "function",
    },
]

EXTENSIBLE_FALLBACK_HANDLER = [
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "contract Safe",
                "name": "safe",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "bytes32",
                "name": "domainSeparator",
                "type": "bytes32",
            },
            {
                "indexed": False,
                "internalType": "contract ISafeSignatureVerifier",
                "name": "verifier",
                "type": "address",
            },
        ],
        "name": "AddedDomainVerifier",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "contract Safe",
                "name": "safe",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "bytes4",
                "name": "interfaceId",
                "type": "bytes4",
            },
        ],
        "name": "AddedInterface",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "contract Safe",
                "name": "safe",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "bytes4",
                "name": "selector",
                "type": "bytes4",
            },
            {
                "indexed": False,
                "internalType": "bytes32",
                "name": "method",
                "type": "bytes32",
            },
        ],
        "name": "AddedSafeMethod",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "contract Safe",
                "name": "safe",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "bytes32",
                "name": "domainSeparator",
                "type": "bytes32",
            },
            {
                "indexed": False,
                "internalType": "contract ISafeSignatureVerifier",
                "name": "oldVerifier",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "contract ISafeSignatureVerifier",
                "name": "newVerifier",
                "type": "address",
            },
        ],
        "name": "ChangedDomainVerifier",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "contract Safe",
                "name": "safe",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "bytes4",
                "name": "selector",
                "type": "bytes4",
            },
            {
                "indexed": False,
                "internalType": "bytes32",
                "name": "oldMethod",
                "type": "bytes32",
            },
            {
                "indexed": False,
                "internalType": "bytes32",
                "name": "newMethod",
                "type": "bytes32",
            },
        ],
        "name": "ChangedSafeMethod",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "contract Safe",
                "name": "safe",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "bytes32",
                "name": "domainSeparator",
                "type": "bytes32",
            },
        ],
        "name": "RemovedDomainVerifier",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "contract Safe",
                "name": "safe",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "bytes4",
                "name": "interfaceId",
                "type": "bytes4",
            },
        ],
        "name": "RemovedInterface",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "contract Safe",
                "name": "safe",
                "type": "address",
            },
            {
                "indexed": False,
                "internalType": "bytes4",
                "name": "selector",
                "type": "bytes4",
            },
        ],
        "name": "RemovedSafeMethod",
        "type": "event",
    },
    {"stateMutability": "nonpayable", "type": "fallback"},
    {
        "inputs": [
            {"internalType": "contract Safe", "name": "", "type": "address"},
            {"internalType": "bytes32", "name": "", "type": "bytes32"},
        ],
        "name": "domainVerifiers",
        "outputs": [
            {
                "internalType": "contract ISafeSignatureVerifier",
                "name": "",
                "type": "address",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "_hash", "type": "bytes32"},
            {"internalType": "bytes", "name": "signature", "type": "bytes"},
        ],
        "name": "isValidSignature",
        "outputs": [{"internalType": "bytes4", "name": "magic", "type": "bytes4"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "uint256[]", "name": "", "type": "uint256[]"},
            {"internalType": "uint256[]", "name": "", "type": "uint256[]"},
            {"internalType": "bytes", "name": "", "type": "bytes"},
        ],
        "name": "onERC1155BatchReceived",
        "outputs": [{"internalType": "bytes4", "name": "", "type": "bytes4"}],
        "stateMutability": "pure",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "bytes", "name": "", "type": "bytes"},
        ],
        "name": "onERC1155Received",
        "outputs": [{"internalType": "bytes4", "name": "", "type": "bytes4"}],
        "stateMutability": "pure",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "bytes", "name": "", "type": "bytes"},
        ],
        "name": "onERC721Received",
        "outputs": [{"internalType": "bytes4", "name": "", "type": "bytes4"}],
        "stateMutability": "pure",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "contract Safe", "name": "", "type": "address"},
            {"internalType": "bytes4", "name": "", "type": "bytes4"},
        ],
        "name": "safeInterfaces",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "contract Safe", "name": "", "type": "address"},
            {"internalType": "bytes4", "name": "", "type": "bytes4"},
        ],
        "name": "safeMethods",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "domainSeparator", "type": "bytes32"},
            {
                "internalType": "contract ISafeSignatureVerifier",
                "name": "newVerifier",
                "type": "address",
            },
        ],
        "name": "setDomainVerifier",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes4", "name": "selector", "type": "bytes4"},
            {"internalType": "bytes32", "name": "newMethod", "type": "bytes32"},
        ],
        "name": "setSafeMethod",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes4", "name": "interfaceId", "type": "bytes4"},
            {"internalType": "bool", "name": "supported", "type": "bool"},
        ],
        "name": "setSupportedInterface",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes4", "name": "_interfaceId", "type": "bytes4"},
            {
                "internalType": "bytes32[]",
                "name": "handlerWithSelectors",
                "type": "bytes32[]",
            },
        ],
        "name": "setSupportedInterfaceBatch",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes4", "name": "interfaceId", "type": "bytes4"}],
        "name": "supportsInterface",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
]

TWAP = [
    {
        "inputs": [
            {
                "internalType": "contract ComposableCoW",
                "name": "_composableCow",
                "type": "address",
            }
        ],
        "stateMutability": "nonpayable",
        "type": "constructor",
    },
    {"inputs": [], "name": "InvalidFrequency", "type": "error"},
    {"inputs": [], "name": "InvalidMinPartLimit", "type": "error"},
    {"inputs": [], "name": "InvalidNumParts", "type": "error"},
    {"inputs": [], "name": "InvalidPartSellAmount", "type": "error"},
    {"inputs": [], "name": "InvalidSameToken", "type": "error"},
    {"inputs": [], "name": "InvalidSpan", "type": "error"},
    {"inputs": [], "name": "InvalidStartTime", "type": "error"},
    {"inputs": [], "name": "InvalidToken", "type": "error"},
    {"inputs": [], "name": "OrderNotValid", "type": "error"},
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "owner",
                "type": "address",
            },
            {
                "components": [
                    {
                        "internalType": "contract IConditionalOrder",
                        "name": "handler",
                        "type": "address",
                    },
                    {"internalType": "bytes32", "name": "salt", "type": "bytes32"},
                    {"internalType": "bytes", "name": "staticInput", "type": "bytes"},
                ],
                "indexed": False,
                "internalType": "struct IConditionalOrder.ConditionalOrderParams",
                "name": "params",
                "type": "tuple",
            },
        ],
        "name": "ConditionalOrderCreated",
        "type": "event",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "owner", "type": "address"},
            {"internalType": "address", "name": "", "type": "address"},
            {"internalType": "bytes32", "name": "ctx", "type": "bytes32"},
            {"internalType": "bytes", "name": "staticInput", "type": "bytes"},
            {"internalType": "bytes", "name": "", "type": "bytes"},
        ],
        "name": "getTradeableOrder",
        "outputs": [
            {
                "components": [
                    {
                        "internalType": "contract IERC20",
                        "name": "sellToken",
                        "type": "address",
                    },
                    {
                        "internalType": "contract IERC20",
                        "name": "buyToken",
                        "type": "address",
                    },
                    {"internalType": "address", "name": "receiver", "type": "address"},
                    {
                        "internalType": "uint256",
                        "name": "sellAmount",
                        "type": "uint256",
                    },
                    {"internalType": "uint256", "name": "buyAmount", "type": "uint256"},
                    {"internalType": "uint32", "name": "validTo", "type": "uint32"},
                    {"internalType": "bytes32", "name": "appData", "type": "bytes32"},
                    {"internalType": "uint256", "name": "feeAmount", "type": "uint256"},
                    {"internalType": "bytes32", "name": "kind", "type": "bytes32"},
                    {
                        "internalType": "bool",
                        "name": "partiallyFillable",
                        "type": "bool",
                    },
                    {
                        "internalType": "bytes32",
                        "name": "sellTokenBalance",
                        "type": "bytes32",
                    },
                    {
                        "internalType": "bytes32",
                        "name": "buyTokenBalance",
                        "type": "bytes32",
                    },
                ],
                "internalType": "struct GPv2Order.Data",
                "name": "order",
                "type": "tuple",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes4", "name": "interfaceId", "type": "bytes4"}],
        "name": "supportsInterface",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "owner", "type": "address"},
            {"internalType": "address", "name": "sender", "type": "address"},
            {"internalType": "bytes32", "name": "_hash", "type": "bytes32"},
            {"internalType": "bytes32", "name": "domainSeparator", "type": "bytes32"},
            {"internalType": "bytes32", "name": "ctx", "type": "bytes32"},
            {"internalType": "bytes", "name": "staticInput", "type": "bytes"},
            {"internalType": "bytes", "name": "offchainInput", "type": "bytes"},
            {
                "components": [
                    {
                        "internalType": "contract IERC20",
                        "name": "sellToken",
                        "type": "address",
                    },
                    {
                        "internalType": "contract IERC20",
                        "name": "buyToken",
                        "type": "address",
                    },
                    {"internalType": "address", "name": "receiver", "type": "address"},
                    {
                        "internalType": "uint256",
                        "name": "sellAmount",
                        "type": "uint256",
                    },
                    {"internalType": "uint256", "name": "buyAmount", "type": "uint256"},
                    {"internalType": "uint32", "name": "validTo", "type": "uint32"},
                    {"internalType": "bytes32", "name": "appData", "type": "bytes32"},
                    {"internalType": "uint256", "name": "feeAmount", "type": "uint256"},
                    {"internalType": "bytes32", "name": "kind", "type": "bytes32"},
                    {
                        "internalType": "bool",
                        "name": "partiallyFillable",
                        "type": "bool",
                    },
                    {
                        "internalType": "bytes32",
                        "name": "sellTokenBalance",
                        "type": "bytes32",
                    },
                    {
                        "internalType": "bytes32",
                        "name": "buyTokenBalance",
                        "type": "bytes32",
                    },
                ],
                "internalType": "struct GPv2Order.Data",
                "name": "",
                "type": "tuple",
            },
        ],
        "name": "verify",
        "outputs": [],
        "stateMutability": "view",
        "type": "function",
    },
]

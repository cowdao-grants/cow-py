.PHONY: codegen web3_codegen orderbook_codegen subgraph_codegen test lint format remove_unused_imports

codegen: web3_codegen orderbook_codegen
# codegen: web3_codegen orderbook_codegen subgraph_codegen

web3_codegen:
	poetry run python -m cowdao_cowpy.codegen.main

orderbook_codegen:
	poetry run datamodel-codegen --url="https://raw.githubusercontent.com/cowprotocol/services/main/crates/orderbook/openapi.yml" --output cowdao_cowpy/order_book/generated/model.py --target-python-version 3.12 --output-model-type pydantic_v2.BaseModel --input-file-type openapi

subgraph_codegen:
	poetry run ariadne-codegen

test:
	poetry run pytest -s

lint:
	poetry run ruff check . --fix

format: remove_unused_imports
	poetry run ruff format

remove_unused_imports:
	poetry run pycln --all .

typecheck:
	poetry run pyright
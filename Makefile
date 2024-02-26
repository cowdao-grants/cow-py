web3_codegen:
	poetry run web3_codegen

orderbook_codegen:
	datamodel-codegen --url https://raw.githubusercontent.com/cowprotocol/services/v2.245.1/crates/orderbook/openapi.yml --output cow_py/order_book/__generated__/model.py --target-python-version 3.12  --output-model-type pydantic_v2.BaseModel --input-file-type openapi

test:
	pytest -s


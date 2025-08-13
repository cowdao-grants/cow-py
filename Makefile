.PHONY: codegen web3_codegen orderbook_codegen subgraph_codegen test lint format remove_unused_imports install

install:
	poetry install

codegen: web3_codegen orderbook_codegen
# codegen: web3_codegen orderbook_codegen subgraph_codegen

web3_codegen:
	poetry run python -m cowdao_cowpy.codegen.main

orderbook_codegen:
	wget -O openapi.yml https://raw.githubusercontent.com/cowprotocol/services/refs/heads/main/crates/orderbook/openapi.yml
	poetry run datamodel-codegen \
		--input openapi.yml \
  		--output cowdao_cowpy/order_book/generated/model.py \
  		--target-python-version 3.12 \
  		--output-model-type pydantic_v2.BaseModel \
  		--base-class cowdao_cowpy.order_book.base.BaseModel \
  		--input-file-type openapi
	poetry run  python cowdao_cowpy/post_process.py openapi.yml cowdao_cowpy/order_book/generated/model.py


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
	poetry run pyright examples tests cowdao_cowpy

doc-check:
	poetry run codespell docs/ README.md
	poetry run mkdocs build --clean

all: 
	make format lint typecheck test


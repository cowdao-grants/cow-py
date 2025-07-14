"""
Post-process OpenAPI spec to update model files with nullable fields.
"""

import sys
import ast
import yaml
from pathlib import Path
from typing import Dict, Set


def extract_nullable_fields(openapi_spec_path: str) -> Dict[str, Set[str]]:
    """Parse OpenAPI spec and extract nullable fields for each schema."""
    with open(openapi_spec_path, "r") as f:
        spec = yaml.safe_load(f)

    nullable_fields_by_class = {}

    components = spec.get("components", {}).get("schemas", {})
    for class_name, schema in components.items():
        if schema.get("type") != "object":
            continue
        properties = schema.get("properties", {})
        for prop_name, prop_attrs in properties.items():
            if prop_attrs.get("nullable") is True:
                if "allOf" in prop_attrs:
                    nullable_fields_by_class.setdefault(class_name, set()).add(
                        prop_name
                    )

    return nullable_fields_by_class


def update_ast_model_file(
    model_file_path: str, nullable_fields_by_class: Dict[str, Set[str]]
) -> None:
    """Update AST of the model file to make fields Optional if marked nullable in OpenAPI."""
    code = Path(model_file_path).read_text()
    tree = ast.parse(code)

    class NullableFieldRewriter(ast.NodeTransformer):
        def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
            nullable_fields = nullable_fields_by_class.get(node.name, set())
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign) and isinstance(
                    stmt.target, ast.Name
                ):
                    field_name = stmt.target.id
                    if field_name in nullable_fields:
                        if isinstance(stmt.annotation, ast.Name):
                            print(
                                f"Making field '{field_name}' Optional in class '{node.name}'"
                            )
                            original_type = stmt.annotation.id
                            stmt.annotation = ast.Subscript(
                                value=ast.Name(id="Optional", ctx=ast.Load()),
                                slice=ast.Name(id=original_type, ctx=ast.Load()),
                                ctx=ast.Load(),
                            )
                            stmt.value = ast.Constant(value=None)
            return node

    tree = NullableFieldRewriter().visit(tree)
    ast.fix_missing_locations(tree)

    patched_code = ast.unparse(tree)

    if "Optional" not in patched_code:
        patched_code = "from typing import Optional\n" + patched_code

    Path(model_file_path).write_text(patched_code)
    print(f"Updated {model_file_path} with optional fields where necessary.")


def main(openapi_spec_path: str, model_file_paths: Set[str]) -> None:
    """Main function to process OpenAPI spec and update model files."""
    nullable_fields_by_class = extract_nullable_fields(openapi_spec_path)

    for model_file_path in model_file_paths:
        update_ast_model_file(model_file_path, nullable_fields_by_class)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: python post_process.py <openapi_spec_path> <model_file_path1> <model_file_path2> ..."
        )
        sys.exit(1)

    openapi_spec_path = sys.argv[1]
    model_file_paths = set(sys.argv[2:])

    main(openapi_spec_path, model_file_paths)
    print("Post-processing completed.")

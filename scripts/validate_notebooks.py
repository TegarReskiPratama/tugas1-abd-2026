"""Validasi statis JSON, format notebook, sintaks, dan import lokal; tanpa eksekusi cell."""

import argparse
import ast
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-unexecuted", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    expected = [
        "01_data_profiling.ipynb", "02_data_cleaning.ipynb", "03_eda_and_insights.ipynb"
    ]
    try:
        import nbformat
    except ImportError:
        nbformat = None
    count = 0
    for name in expected:
        path = root / "notebooks" / name
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("nbformat") != 4 or not payload.get("cells"):
            raise ValueError(f"Format notebook tidak valid atau kosong: {name}")
        if nbformat is not None:
            nbformat.validate(nbformat.from_dict(payload))
        seen_ids = set()
        for index, cell in enumerate(payload["cells"]):
            cell_id = cell.get("id")
            if not cell_id or cell_id in seen_ids:
                raise ValueError(f"Cell ID kosong/duplikat: {name}, cell {index}")
            seen_ids.add(cell_id)
            source = cell["source"]
            source = source if isinstance(source, str) else "".join(source)
            if cell["cell_type"] == "code":
                tree = ast.parse(source, filename=f"{name}:cell{index}")
                count += 1
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("src."):
                        module = root.joinpath(*node.module.split(".")).with_suffix(".py")
                        if not module.is_file():
                            raise ValueError(f"Modul lokal tidak tersedia: {node.module}")
                        module_tree = ast.parse(module.read_text(encoding="utf-8"))
                        symbols = {
                            item.name for item in module_tree.body
                            if isinstance(item, (ast.FunctionDef, ast.ClassDef))
                        }
                        for item in module_tree.body:
                            if isinstance(item, ast.Assign):
                                symbols.update(target.id for target in item.targets if isinstance(target, ast.Name))
                        unknown = [alias.name for alias in node.names if alias.name not in symbols]
                        if unknown:
                            raise ValueError(f"Import lokal tidak dikenal: {node.module}: {unknown}")
                if args.require_unexecuted and (
                    cell.get("execution_count") is not None or cell.get("outputs")
                ):
                    raise ValueError(f"Notebook harus belum dieksekusi: {name}, cell {index}")
                if "TODO" in source or "kolom_numerik" in source or "id_unik" in source:
                    raise ValueError(f"Placeholder tersisa: {name}, cell {index}")
        print(f"OK {name}: {len(payload['cells'])} cell")
    for folder in ("src", "scripts"):
        for path in root.joinpath(folder).glob("*.py"):
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    detail = "dengan nbformat" if nbformat is not None else "dengan JSON dan AST; nbformat belum terpasang"
    print(f"Validasi statis lulus ({count} code cell), {detail}. Cell tidak dieksekusi.")


if __name__ == "__main__":
    main()

"""One-off smoke test for Hugging Face dataset access. Delete after use."""
import os
from pathlib import Path

for line in Path(".env").read_text().splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

token = os.environ.get("HF_TOKEN", "")
if not token:
    raise SystemExit("STATUS: no HF_TOKEN found in .env")

print("STATUS: HF_TOKEN present (value not shown)")

from huggingface_hub import HfApi, list_repo_files

api = HfApi(token=token)
repo_id = "FlyRank/internship-warehouse"
info = api.dataset_info(repo_id)
print(f"DATASET: {repo_id}")
print(f"  gated: {info.gated}")
print(f"  private: {info.private}")

files = list_repo_files(repo_id, repo_type="dataset", token=token)
print(f"  file_count: {len(files)}")
print("  sample_paths:")
for p in sorted(files)[:5]:
    print(f"    - {p}")

import duckdb

con = duckdb.connect()
con.execute(f"CREATE OR REPLACE SECRET hf (TYPE huggingface, TOKEN '{token}')")
n = con.execute(
    "SELECT COUNT(*) FROM read_parquet("
    "'hf://datasets/FlyRank/internship-warehouse/dim_clients/*.parquet'"
    ")"
).fetchone()[0]
print(f"DUCKDB: dim_clients row count = {n}")
con.close()
print("RESULT: dataset access OK")

import os
from sqlalchemy import create_engine, text

def load_env_file(path: str) -> None:
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

load_env_file(os.path.join(os.path.dirname(__file__), "..", ".env"))
url = os.getenv("DATABASE_URL")
print("DB", url)
engine = create_engine(url)
with engine.connect() as conn:
    for table in ["pipelines", "pipeline_runs", "pipeline_run_steps", "pipeline_events"]:
        rows = conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns WHERE table_name=:table ORDER BY ordinal_position"
            ),
            {"table": table}
        )
        print(table, [r[0] for r in rows])

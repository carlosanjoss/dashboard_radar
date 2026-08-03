import subprocess
import sys
from pathlib import Path


APP_PATH = Path(__file__).resolve().parent / "app.py"


if __name__ == "__main__":
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(APP_PATH),
            "--server.port",
            "8501",
        ],
        check=True,
    )

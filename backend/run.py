import os
import sys
from pathlib import Path
import uvicorn

# Ensure backend root is in sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "127.0.0.1")
    print(f"Starting AgriShield AI Crop Disease Server on http://{host}:{port} ...")
    uvicorn.run("app.main:app", host=host, port=port, reload=False, log_level="info")

import os
import sys
from pathlib import Path
import uvicorn

root_dir = Path(__file__).resolve().parent
backend_dir = root_dir / "backend"

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

def main():
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "127.0.0.1")
    
    print("=" * 65)
    print("  AGRISHIELD - AI CROP DISEASE DETECTION SYSTEM")
    print("=" * 65)
    print(f"  • Web Application URL : http://{host}:{port}")
    print(f"  • Interactive API Docs: http://{host}:{port}/docs")
    print(f"  • ML Inference Engine : PyTorch MobileNetV3 (CPU)")
    print(f"  • Database Persistence: SQLite (crop_disease.db)")
    print("=" * 65)
    print("  Server is running... Press Ctrl+C to stop.\n")
    
    uvicorn.run("app.main:app", host=host, port=port, reload=False, log_level="info")

if __name__ == "__main__":
    main()

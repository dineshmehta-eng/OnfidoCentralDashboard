import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import uvicorn
uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, log_level="info", workers=1)

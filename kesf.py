

import sys
import uvicorn
from loguru import logger

if __name__ == "__main__":
    if sys.version_info < (3, 11):
        print("Error: KƏŞF requires Python 3.11 or higher.")
        sys.exit(1)
        
    print("KƏŞF Web Serveri işə salınır...")
    print("Brauzer avtomatik açılacaq. Əgər açılmazsa, http://127.0.0.1:8000 ünvanına daxil olun.")
    
    try:
        uvicorn.run("web:app", host="127.0.0.1", port=8000, reload=False, log_level="warning")
    except KeyboardInterrupt:
        print("\nİstifadəçi tərəfindən dayandırıldı.")
        sys.exit(0)

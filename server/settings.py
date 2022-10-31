import os

PORT: int = 8000
DOMAIN: str = '192.168.0.174'
OUTPUT_DIR: str= 'output'
URL_STORAGE_PATH: str = os.path.join(OUTPUT_DIR, 'urls.json')
PAGES_HOME: str = os.path.join("server", "client", "dist")
LOCAL_PAGES_HOME: str = os.path.join("client", "dist")
DB_NAME: str = 'url_compressor'
USER_TBL: str = 'users'
URL_TBL: str = 'urls'
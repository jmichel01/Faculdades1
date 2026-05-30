import pytest
import os
import warnings
from config.settings import Settings
from database.manager import DatabaseManager

warnings.filterwarnings("ignore", category=DeprecationWarning, module="pulp")

@pytest.fixture(scope="session", autouse=True)
def setup_test_db() -> None:
    original_db = Settings.DB_PATH
    test_db_path = Settings.BASE_DIR / "data" / "smart_routes_test.db"
    
    Settings.DB_PATH = test_db_path
    Settings.initialize_directories()
    DatabaseManager.initialize_database()
    
    yield
    
    try:
        if test_db_path.exists():
            import time
            time.sleep(0.3)
            os.remove(test_db_path)
    except Exception as e:
        print(f"Test DB cleanup warning: {e}")
        
    Settings.DB_PATH = original_db
#A

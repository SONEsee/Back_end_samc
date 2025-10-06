# SAMCSYS/backup.py - FINAL WORKING VERSION
import pyodbc
import os
from django.conf import settings
from datetime import datetime

def backup_database(backup_path=None):
    """
    Backup SQL Server database
    Returns: (file_path, success, message)
    """
    conn = None
    cursor = None
    
    try:
        # Get database connection details from settings
        db_name = settings.DATABASES['default']['NAME']
        db_user = settings.DATABASES['default']['USER']
        db_password = settings.DATABASES['default']['PASSWORD']
        db_host = settings.DATABASES['default']['HOST']
        driver = settings.DATABASES['default']['OPTIONS'].get('driver', 'ODBC Driver 17 for SQL Server')

        # Create backup directory and filename if not provided
        if not backup_path:
            backup_dir = os.path.join(settings.BASE_DIR, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f'backup_{db_name}_{timestamp}.bak')

        # Connection string with extended timeouts
        conn_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={db_host};"
            f"DATABASE=master;"  # Connect to master for backup operations
            f"UID={db_user};"
            f"PWD={db_password};"
            f"Connection Timeout=60;"
            f"Login Timeout=60;"
            f"Encrypt=no;"
            f"TrustServerCertificate=yes;"
        )
        
        # CRITICAL: autocommit=True is required for BACKUP operations
        # SQL Server doesn't allow BACKUP inside transactions
        conn = pyodbc.connect(conn_str, autocommit=True, timeout=60)
        cursor = conn.cursor()

        # SQL Server BACKUP command with compression
        backup_query = f"""
        BACKUP DATABASE [{db_name}]
        TO DISK = N'{backup_path}'
        WITH FORMAT, 
             INIT, 
             NAME = N'Full Backup of {db_name}',
             COMPRESSION,
             STATS = 10;
        """
        
        # Execute backup
        cursor.execute(backup_query)
        
        # Clean up
        cursor.close()
        conn.close()

        return backup_path, True, "Database backup completed successfully."

    except pyodbc.Error as e:
        error_msg = f"Database error: {str(e)}"
        print(f"Backup failed: {error_msg}")
        return None, False, error_msg
        
    except Exception as e:
        error_msg = f"Backup failed: {str(e)}"
        print(f"Unexpected error: {error_msg}")
        return None, False, error_msg

    finally:
        # Ensure connections are closed
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass
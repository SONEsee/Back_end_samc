import os
import pyodbc
from datetime import datetime, timedelta
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class BackupService:
    """Handles SQL Server database backup operations"""
    
    def __init__(self):
        self.config = settings.BACKUP_CONFIG
        self.db_config = settings.DATABASES['default']
        
    def _get_connection(self):
        """Create database connection with proper timeout"""
        driver = self.db_config['OPTIONS'].get('driver', 'ODBC Driver 17 for SQL Server')
        conn_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={self.db_config['HOST']};"
            f"DATABASE=master;"
            f"UID={self.db_config['USER']};"
            f"PWD={self.db_config['PASSWORD']};"
            f"Connection Timeout=60;"
            f"Login Timeout=60;"
            f"Encrypt=no;"
            f"TrustServerCertificate=yes;"
        )
        return pyodbc.connect(conn_str, autocommit=True, timeout=60)
    
    def _validate_path(self, path):
        """Validate and prepare backup path"""
        if not path:
            path = self.config['DEFAULT_PATH']
        
        # Security: Prevent path traversal
        path = os.path.abspath(path)
        allowed_paths = [self.config['DEFAULT_PATH']]
        
        if not any(path.startswith(allowed) for allowed in allowed_paths):
            raise ValueError("Invalid backup path")
        
        # Create directory if needed
        os.makedirs(path, exist_ok=True)
        return path
    
    def _generate_filename(self):
        """Generate unique backup filename"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        db_name = self.db_config['NAME']
        return f"backup_{db_name}_{timestamp}.bak"
    
    def _cleanup_old_backups(self, directory):
        """Remove old backup files"""
        try:
            cutoff = datetime.now() - timedelta(days=self.config['MAX_FILE_AGE_DAYS'])
            
            for file in os.listdir(directory):
                if file.endswith('.bak'):
                    filepath = os.path.join(directory, file)
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    if file_time < cutoff:
                        os.remove(filepath)
                        logger.info(f"Removed old backup: {file}")
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")
    
    def create_backup(self, custom_path=None):
        """
        Create database backup
        Returns: dict with status, filepath, and message
        """
        conn = None
        cursor = None
        
        try:
            # Validate and prepare path
            backup_dir = self._validate_path(custom_path)
            filename = self._generate_filename()
            filepath = os.path.join(backup_dir, filename)
            
            # Clean up old backups
            self._cleanup_old_backups(backup_dir)
            
            # Connect to database
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Build backup query
            db_name = self.db_config['NAME']
            compression = "COMPRESSION," if self.config['COMPRESSION'] else ""
            
            backup_query = f"""
            BACKUP DATABASE [{db_name}]
            TO DISK = N'{filepath}'
            WITH FORMAT, 
                 INIT, 
                 NAME = N'Full Backup of {db_name}',
                 {compression}
                 STATS = 10;
            """
            
            # Execute backup
            cursor.execute(backup_query)
            
            # Verify file was created
            if not os.path.exists(filepath):
                raise Exception("Backup file was not created")
            
            filesize = os.path.getsize(filepath)
            
            return {
                'success': True,
                'filepath': filepath,
                'filename': filename,
                'size': filesize,
                'message': 'Backup completed successfully'
            }
            
        except pyodbc.Error as e:
            logger.error(f"Database backup error: {e}")
            return {
                'success': False,
                'filepath': None,
                'message': f"Database error: {str(e)}"
            }
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return {
                'success': False,
                'filepath': None,
                'message': str(e)
            }
            
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

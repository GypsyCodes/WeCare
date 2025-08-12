"""
Backup and maintenance service
"""
import os
import subprocess
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any
import asyncio

from app.services.celery_app import celery_app
from app.core.config import settings


@celery_app.task(name="app.services.backup_service.backup_database_task")
def backup_database_task():
    """
    Create database backup using mysqldump
    """
    try:
        # Create backups directory
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"wecare_backup_{timestamp}.sql"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Build mysqldump command
        cmd = [
            "mysqldump",
            f"--host={settings.DB_HOST}",
            f"--port={settings.DB_PORT}",
            f"--user={settings.DB_USER}",
            f"--password={settings.DB_PASSWORD}",
            "--single-transaction",
            "--routines",
            "--triggers",
            settings.DB_NAME
        ]
        
        # Execute backup
        with open(backup_path, 'w') as backup_file:
            result = subprocess.run(
                cmd,
                stdout=backup_file,
                stderr=subprocess.PIPE,
                text=True,
                timeout=1800  # 30 minute timeout
            )
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"mysqldump failed: {result.stderr}",
                "timestamp": timestamp
            }
        
        # Get backup file size
        backup_size = os.path.getsize(backup_path)
        
        # Compress backup
        compressed_path = f"{backup_path}.gz"
        with open(backup_path, 'rb') as f_in:
            import gzip
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remove uncompressed file
        os.remove(backup_path)
        
        # Get compressed size
        compressed_size = os.path.getsize(compressed_path)
        
        # Clean old backups (keep last 7 days)
        cleanup_old_backups(backup_dir, days_to_keep=7)
        
        return {
            "success": True,
            "backup_file": compressed_path,
            "original_size": backup_size,
            "compressed_size": compressed_size,
            "timestamp": timestamp,
            "compression_ratio": f"{(1 - compressed_size/backup_size)*100:.1f}%"
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Backup timeout - operation took too long",
            "timestamp": timestamp
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": timestamp
        }


def cleanup_old_backups(backup_dir: str, days_to_keep: int = 7):
    """Clean up old backup files"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        for filename in os.listdir(backup_dir):
            if filename.startswith("wecare_backup_") and filename.endswith(".sql.gz"):
                file_path = os.path.join(backup_dir, filename)
                file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_modified < cutoff_date:
                    os.remove(file_path)
                    print(f"Removed old backup: {filename}")
    
    except Exception as e:
        print(f"Error cleaning old backups: {e}")


@celery_app.task(name="app.services.backup_service.cleanup_old_logs_task")
def cleanup_old_logs_task():
    """
    Clean up old log entries from database
    """
    from app.core.database import AsyncSessionLocal
    from app.core.models import Log
    from sqlalchemy import select, delete
    import asyncio
    
    async def _cleanup():
        async with AsyncSessionLocal() as db:
            try:
                # Delete logs older than 90 days
                cutoff_date = datetime.now() - timedelta(days=90)
                
                # Count logs to be deleted
                count_query = select(Log).where(Log.data_hora < cutoff_date)
                count_result = await db.execute(count_query)
                logs_to_delete = len(count_result.scalars().all())
                
                if logs_to_delete > 0:
                    # Delete old logs
                    delete_query = delete(Log).where(Log.data_hora < cutoff_date)
                    await db.execute(delete_query)
                    await db.commit()
                
                return {
                    "success": True,
                    "logs_deleted": logs_to_delete,
                    "cutoff_date": cutoff_date.isoformat()
                }
                
            except Exception as e:
                await db.rollback()
                return {
                    "success": False,
                    "error": str(e)
                }
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(_cleanup())
        return result
    finally:
        loop.close()


@celery_app.task(name="app.services.backup_service.cleanup_old_documents_task")
def cleanup_old_documents_task():
    """
    Clean up orphaned document files
    """
    from app.core.database import AsyncSessionLocal
    from app.core.models import Documento
    from sqlalchemy import select
    import asyncio
    
    async def _cleanup():
        async with AsyncSessionLocal() as db:
            try:
                # Get all document records
                result = await db.execute(select(Documento))
                documents = result.scalars().all()
                
                existing_paths = set()
                orphaned_files = []
                
                # Check which files exist in database
                for doc in documents:
                    if doc.arquivo_path and os.path.exists(doc.arquivo_path):
                        existing_paths.add(doc.arquivo_path)
                
                # Walk through upload directory
                upload_path = settings.UPLOAD_PATH
                if os.path.exists(upload_path):
                    for root, dirs, files in os.walk(upload_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            
                            # Check if file is referenced in database
                            if file_path not in existing_paths:
                                # Check if file is older than 30 days
                                file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                                if file_modified < datetime.now() - timedelta(days=30):
                                    orphaned_files.append(file_path)
                
                # Delete orphaned files
                deleted_count = 0
                for file_path in orphaned_files:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except OSError:
                        pass  # File might be locked or already deleted
                
                return {
                    "success": True,
                    "orphaned_files_deleted": deleted_count,
                    "total_documents": len(documents)
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(_cleanup())
        return result
    finally:
        loop.close()


@celery_app.task(name="app.services.backup_service.system_health_check_task")
def system_health_check_task():
    """
    Perform system health checks
    """
    health_status = {
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }
    
    # Check disk space
    try:
        disk_usage = shutil.disk_usage(".")
        free_gb = disk_usage.free / (1024**3)
        total_gb = disk_usage.total / (1024**3)
        usage_percent = ((total_gb - free_gb) / total_gb) * 100
        
        health_status["checks"]["disk_space"] = {
            "status": "healthy" if usage_percent < 85 else "warning" if usage_percent < 95 else "critical",
            "free_gb": round(free_gb, 2),
            "total_gb": round(total_gb, 2),
            "usage_percent": round(usage_percent, 2)
        }
    except Exception as e:
        health_status["checks"]["disk_space"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check upload directory
    try:
        upload_dir = settings.UPLOAD_PATH
        upload_exists = os.path.exists(upload_dir)
        upload_writable = os.access(upload_dir, os.W_OK) if upload_exists else False
        
        health_status["checks"]["upload_directory"] = {
            "status": "healthy" if upload_exists and upload_writable else "critical",
            "exists": upload_exists,
            "writable": upload_writable,
            "path": upload_dir
        }
    except Exception as e:
        health_status["checks"]["upload_directory"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check database connectivity
    try:
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import text
        import asyncio
        
        async def _check_db():
            async with AsyncSessionLocal() as db:
                result = await db.execute(text("SELECT 1"))
                return result.scalar() == 1
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            db_connected = loop.run_until_complete(_check_db())
            health_status["checks"]["database"] = {
                "status": "healthy" if db_connected else "critical",
                "connected": db_connected
            }
        finally:
            loop.close()
            
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Overall health status
    statuses = [check.get("status") for check in health_status["checks"].values()]
    if "critical" in statuses or "error" in statuses:
        overall_status = "unhealthy"
    elif "warning" in statuses:
        overall_status = "warning"
    else:
        overall_status = "healthy"
    
    health_status["overall_status"] = overall_status
    
    return health_status 
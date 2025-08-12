#!/usr/bin/env python3
"""
Celery Worker Entry Point
Run this script to start the Celery worker
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.celery_app import celery_app


def main():
    """Main entry point for Celery worker"""
    print("🚀 Starting We Care Celery Worker...")
    print(f"📍 Project root: {project_root}")
    
    # Worker configuration
    worker_config = {
        'loglevel': 'info',
        'concurrency': 4,
        'queues': ['documents', 'notifications', 'maintenance', 'celery'],
        'beat': False,  # Set to True if you want to run beat scheduler
    }
    
    print(f"🔧 Worker configuration:")
    for key, value in worker_config.items():
        print(f"   {key}: {value}")
    
    print("\n" + "="*60)
    print("We Care - Celery Worker")
    print("Processing background tasks... 🔄")
    print("="*60 + "\n")
    
    # Start worker
    celery_app.worker_main([
        'worker',
        '--loglevel', worker_config['loglevel'],
        '--concurrency', str(worker_config['concurrency']),
        '--queues', ','.join(worker_config['queues']),
    ])


if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Celery Beat Scheduler Entry Point
Run this script to start the Celery beat scheduler for periodic tasks
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.celery_app import celery_app


def main():
    """Main entry point for Celery beat scheduler"""
    print("🚀 Starting We Care Celery Beat Scheduler...")
    print(f"📍 Project root: {project_root}")
    
    # Beat configuration
    beat_config = {
        'loglevel': 'info',
        'scheduler': 'celery.beat:PersistentScheduler',
    }
    
    print(f"🔧 Beat configuration:")
    for key, value in beat_config.items():
        print(f"   {key}: {value}")
    
    print("\nScheduled tasks:")
    for task_name, task_config in celery_app.conf.beat_schedule.items():
        schedule = task_config.get('schedule')
        if isinstance(schedule, (int, float)):
            schedule_str = f"every {schedule} seconds"
        else:
            schedule_str = str(schedule)
        print(f"   📅 {task_name}: {schedule_str}")
    
    print("\n" + "="*60)
    print("We Care - Celery Beat Scheduler")
    print("Managing periodic tasks... ⏰")
    print("="*60 + "\n")
    
    # Start beat scheduler
    celery_app.start([
        'beat',
        '--loglevel', beat_config['loglevel'],
        '--scheduler', beat_config['scheduler'],
    ])


if __name__ == "__main__":
    main() 
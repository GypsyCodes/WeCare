#!/usr/bin/env python3
"""
Development Environment Setup Script
Run this script to initialize the development environment
"""
import os
import sys
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.core.database import AsyncSessionLocal, engine
from app.core.models import Base, Usuario, PerfilEnum, StatusUsuarioEnum
from app.core.security import get_password_hash
from sqlalchemy import select


async def create_tables():
    """Create database tables"""
    print("📊 Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully!")


async def create_admin_user():
    """Create default admin user if not exists"""
    print("👤 Checking for admin user...")
    
    admin_email = "admin@wecare.com"
    admin_cpf = "000.000.000-00"
    
    async with AsyncSessionLocal() as db:
        # Check if admin already exists
        result = await db.execute(
            select(Usuario).where(Usuario.email == admin_email)
        )
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print(f"ℹ️  Admin user already exists: {admin_email}")
            return existing_admin
        
        # Create admin user
        admin_user = Usuario(
            nome="Administrador",
            email=admin_email,
            cpf=admin_cpf,
            senha_hash=get_password_hash("admin123"),  # Default password
            perfil=PerfilEnum.ADMINISTRADOR,
            status=StatusUsuarioEnum.ATIVO
        )
        
        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)
        
        print(f"✅ Admin user created successfully!")
        print(f"   Email: {admin_email}")
        print(f"   Password: admin123")
        print(f"   ⚠️  REMEMBER to change the password after first login!")
        
        return admin_user


def create_directories():
    """Create required directories"""
    print("📁 Creating required directories...")
    
    directories = [
        settings.UPLOAD_PATH,
        "logs",
        "backups",
        "media",
        "static"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(exist_ok=True, parents=True)
        print(f"   📂 {dir_path.absolute()}")
    
    print("✅ Directories created successfully!")


def create_env_file():
    """Create .env file from .env.example if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("ℹ️  .env file already exists")
        return
    
    if not env_example.exists():
        print("⚠️  .env.example file not found")
        return
    
    # Copy .env.example to .env
    import shutil
    shutil.copy2(env_example, env_file)
    
    print("✅ .env file created from .env.example")
    print("⚠️  IMPORTANT: Edit .env file with your configuration before running the application!")


async def check_database_connection():
    """Check database connection"""
    print("🔗 Testing database connection...")
    
    try:
        async with AsyncSessionLocal() as db:
            from sqlalchemy import text
            result = await db.execute(text("SELECT 1"))
            if result.scalar() == 1:
                print("✅ Database connection successful!")
                return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def print_welcome_message():
    """Print welcome message with next steps"""
    print("\n" + "="*80)
    print("🎉 We Care Development Environment Setup Complete!")
    print("="*80)
    
    print("\n📋 Next Steps:")
    print("1. Review and edit the .env file with your configuration")
    print("2. Ensure MySQL server is running")
    print("3. Ensure Redis server is running (for Celery)")
    print("4. Install system dependencies (Tesseract OCR)")
    print("5. Run database migrations: alembic upgrade head")
    print("6. Start the application: python run.py")
    print("7. Start Celery worker: python celery_worker.py")
    print("8. Start Celery beat: python celery_beat.py")
    
    print("\n🌐 Access URLs:")
    print(f"   API: http://localhost:8000")
    print(f"   Docs: http://localhost:8000/docs")
    print(f"   ReDoc: http://localhost:8000/redoc")
    
    print("\n👤 Default Admin User:")
    print("   Email: admin@wecare.com")
    print("   Password: admin123")
    print("   ⚠️  Change this password after first login!")
    
    print("\n🔧 Development Commands:")
    print("   python run.py                 # Start API server")
    print("   python celery_worker.py       # Start Celery worker")
    print("   python celery_beat.py         # Start Celery beat scheduler")
    print("   alembic revision --autogenerate # Create migration")
    print("   alembic upgrade head          # Apply migrations")
    
    print("\n💡 Pro Tips:")
    print("   - Use different terminal windows for API, worker, and beat")
    print("   - Check logs/ directory for application logs")
    print("   - Use /docs endpoint to test API endpoints")
    print("   - Monitor Celery tasks with Flower (optional)")
    
    print("="*80)


async def main():
    """Main setup function"""
    print("🚀 Setting up We Care Development Environment...")
    print(f"📍 Project root: {project_root}")
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Check database connection
    db_connected = await check_database_connection()
    
    if db_connected:
        # Create tables
        await create_tables()
        
        # Create admin user
        await create_admin_user()
    else:
        print("⚠️  Skipping database setup due to connection issues")
        print("   Please check your database configuration and try again")
    
    # Print welcome message
    print_welcome_message()


if __name__ == "__main__":
    asyncio.run(main())
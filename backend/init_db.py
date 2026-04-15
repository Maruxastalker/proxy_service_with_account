"""
Скрипт для инициализации базы данных тестовыми данными.
Запускать после применения миграций.
"""

import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import SessionLocal
from src.models.virtual_machine import VirtualMachine
from src.models.user import User
from src.config import settings


def init_virtual_machines(db):
    """Создание тестовых виртуальных машин"""
    
    count = db.query(VirtualMachine).count()
    if count > 0:
        print(f"✅ В базе уже есть {count} VM. Пропускаем создание.")
        return
    
    vms = [
        VirtualMachine(
            name="Proxy Europe",
            host="eu.proxy.example.com",
            port=3128,
            protocol="HTTP",
            is_active=True,
            current_user_id=None
        ),
        VirtualMachine(
            name="Proxy USA",
            host="us.proxy.example.com",
            port=1080,
            protocol="SOCKS5",
            is_active=True,
            current_user_id=None
        ),
        VirtualMachine(
            name="Proxy Asia",
            host="asia.proxy.example.com",
            port=8080,
            protocol="HTTPS",
            is_active=True,
            current_user_id=None
        ),
        VirtualMachine(
            name="Proxy Local Test",
            host="127.0.0.1",
            port=8888,
            protocol="HTTP",
            is_active=True,
            current_user_id=None
        ),
    ]
    
    for vm in vms:
        db.add(vm)
    
    db.commit()
    print(f"✅ Создано {len(vms)} виртуальных машин:")
    for vm in vms:
        print(f"   - {vm.name}: {vm.host}:{vm.port} ({vm.protocol})")


def main():
    print("=" * 50)
    print("Инициализация базы данных")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        init_virtual_machines(db)

        print("=" * 50)
        print("✅ Инициализация завершена успешно!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        db.rollback()
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
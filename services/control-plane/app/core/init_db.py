"""Database initialization with default data."""
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User
from app.models.role import user_roles


def init_db() -> None:
    """Initialize database with default organization, roles, and admin user."""
    db: Session = SessionLocal()
    try:
        # Create default organization if it doesn't exist
        org = db.query(Organization).filter(Organization.name == "Default Organization").first()
        if not org:
            org = Organization(name="Default Organization")
            db.add(org)
            db.commit()
            db.refresh(org)
            print("✓ Created default organization")

        # Create default roles if they don't exist
        role_names = [
            ("admin", "Administrator with full access"),
            ("user", "Regular user"),
            ("viewer", "Read-only user"),
        ]
        roles = {}
        for name, description in role_names:
            role = db.query(Role).filter(Role.name == name).first()
            if not role:
                role = Role(name=name, description=description)
                db.add(role)
            roles[name] = role
        db.commit()

        # Refresh to get IDs
        for name in roles:
            db.refresh(roles[name])

        # Create default admin user if it doesn't exist
        default_username = settings.DEFAULT_ADMIN_USERNAME
        default_password = settings.DEFAULT_ADMIN_PASSWORD

        admin_user = db.query(User).filter(User.username == default_username).first()
        if not admin_user:
            admin_user = User(
                email="admin@qatron.example",
                username=default_username,
                hashed_password=get_password_hash(default_password),
                full_name="QAtron Administrator",
                is_active=True,
                organization_id=org.id,
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

            # Assign admin role
            admin_role = roles["admin"]
            db.execute(user_roles.insert().values(user_id=admin_user.id, role_id=admin_role.id))
            db.commit()
            print(f"✓ Created default admin user (username: {default_username}, password: {default_password})")

    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

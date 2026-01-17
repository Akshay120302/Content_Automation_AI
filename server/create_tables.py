"""
Database initialization script
Run this script to create all database tables
"""
from app.database.database import Base, engine
from app.models import User, Plan, Subscription, RefreshToken, OAuthAccount

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully!")
    
    # Print created tables
    print("\nCreated tables:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")

if __name__ == "__main__":
    create_tables()

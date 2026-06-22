import os
import uuid
from datetime import datetime, timedelta
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

# Set up the environment similar to bootstrap_app
import dotenv
config_path = os.environ.get(
    "CONFIG_PATH", os.path.join(os.path.dirname(__file__), os.pardir, ".env_file")
)
dotenv.load_dotenv(config_path)

from web_app.app import create_app
from web_app_models import User, Role, RolesUsers
from auctions_infrastructure.models import auctions, bids
from shipping_infrastructure.models import packages
from shipping.domain.value_objects import PackageStatus
from flask_security.utils import hash_password

def seed_db():
    print("Starting database seeding...")
    
    app = create_app()
    from main.modules import RequestScope
    from sqlalchemy.orm import Session
    from sqlalchemy.engine import Connection

    with app.app_context():
        request_scope = app.injector.get(RequestScope)
        request_scope.enter()
        try:
            session = app.injector.get(Session)
            conn = app.injector.get(Connection)
            # 1. Seed Roles
            print("Seeding Roles...")
            admin_role = session.query(Role).filter_by(name="admin").first()
            if not admin_role:
                admin_role = Role(name="admin", description="Admin Role")
                session.add(admin_role)
            
            user_role = session.query(Role).filter_by(name="user").first()
            if not user_role:
                user_role = Role(name="user", description="Regular User Role")
                session.add(user_role)

            session.commit()

            # 2. Seed Users
            print("Seeding Users...")
            mock_users_data = [
                {"id": 1, "email": "admin@cleanarchitecture.io", "password": "password123", "active": True},
                {"id": 2, "email": "buyer@cleanarchitecture.io", "password": "password123", "active": True},
                {"id": 3, "email": "seller@cleanarchitecture.io", "password": "password123", "active": True},
            ]

            mock_users = {}
            for user_data in mock_users_data:
                user = session.query(User).filter_by(email=user_data["email"]).first()
                if not user:
                    user = User(
                        id=user_data["id"],
                        email=user_data["email"],
                        password=hash_password(user_data["password"]),
                        active=user_data["active"],
                        confirmed_at=datetime.utcnow()
                    )
                    session.add(user)
                else:
                    # Update password and active status
                    user.password = hash_password(user_data["password"])
                    user.active = user_data["active"]
                mock_users[user_data["email"]] = user

            session.commit()

            # Assign roles
            if admin_role not in mock_users["admin@cleanarchitecture.io"].roles:
                mock_users["admin@cleanarchitecture.io"].roles.append(admin_role)
            if user_role not in mock_users["buyer@cleanarchitecture.io"].roles:
                mock_users["buyer@cleanarchitecture.io"].roles.append(user_role)
            if user_role not in mock_users["seller@cleanarchitecture.io"].roles:
                mock_users["seller@cleanarchitecture.io"].roles.append(user_role)
            
            session.commit()

            # 3. Seed Auctions (Core Table)
            print("Seeding Auctions...")
            
            from sqlalchemy.dialects.postgresql import insert as pg_insert
            
            now = datetime.utcnow()
            auctions_data = [
                {
                    "id": 1,
                    "title": "Vintage Rolex Watch",
                    "starting_price": 5000.0,
                    "current_price": 5500.0,
                    "ends_at": now + timedelta(days=5),
                    "ended": False
                },
                {
                    "id": 2,
                    "title": "Classic Car - Ford Mustang 1969",
                    "starting_price": 20000.0,
                    "current_price": 20000.0,
                    "ends_at": now + timedelta(days=2),
                    "ended": False
                },
                {
                    "id": 3,
                    "title": "Signed Baseball",
                    "starting_price": 100.0,
                    "current_price": 350.0,
                    "ends_at": now - timedelta(days=1),
                    "ended": True
                }
            ]

            stmt = pg_insert(auctions).values(auctions_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_={
                    "title": stmt.excluded.title,
                    "starting_price": stmt.excluded.starting_price,
                    "current_price": stmt.excluded.current_price,
                    "ends_at": stmt.excluded.ends_at,
                    "ended": stmt.excluded.ended
                }
            )
            conn.execute(stmt)

            # 4. Seed Bids
            print("Seeding Bids...")
            bids_data = [
                {"id": 1, "amount": 5200.0, "bidder_id": 2, "auction_id": 1},
                {"id": 2, "amount": 5500.0, "bidder_id": 3, "auction_id": 1},
                {"id": 3, "amount": 150.0, "bidder_id": 2, "auction_id": 3},
                {"id": 4, "amount": 350.0, "bidder_id": 3, "auction_id": 3},
            ]

            stmt = pg_insert(bids).values(bids_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_={
                    "amount": stmt.excluded.amount,
                    "bidder_id": stmt.excluded.bidder_id,
                    "auction_id": stmt.excluded.auction_id
                }
            )
            conn.execute(stmt)

            # 5. Seed Packages
            print("Seeding Packages...")
            # We must use proper package status Enum matching
            packages_data = [
                {
                    "uuid": "11111111-1111-1111-1111-111111111111",
                    "item_identifier": "pkg-1",
                    "consignee_id": 3, # seller id
                    "street": "123 Main St",
                    "house_number": "1A",
                    "city": "Springfield",
                    "state": "IL",
                    "zip_code": "62701",
                    "country": "USA",
                    "status": PackageStatus.SHIPPED
                },
                {
                    "uuid": "22222222-2222-2222-2222-222222222222",
                    "item_identifier": "pkg-2",
                    "consignee_id": 2, # buyer id
                    "street": "456 Oak St",
                    "house_number": "2B",
                    "city": "Metropolis",
                    "state": "NY",
                    "zip_code": "10001",
                    "country": "USA",
                    "status": PackageStatus.CREATED
                }
            ]

            # Since the packages uses a stringified UUID and standard Enum, we need to handle postgresql insert
            stmt = pg_insert(packages).values(packages_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=['uuid'],
                set_={
                    "item_identifier": stmt.excluded.item_identifier,
                    "consignee_id": stmt.excluded.consignee_id,
                    "street": stmt.excluded.street,
                    "house_number": stmt.excluded.house_number,
                    "city": stmt.excluded.city,
                    "state": stmt.excluded.state,
                    "zip_code": stmt.excluded.zip_code,
                    "country": stmt.excluded.country,
                    "status": stmt.excluded.status
                }
            )
            conn.execute(stmt)
            
            # Reset PostgreSQL sequences so new inserts don't fail with duplicate key errors
            print("Resetting primary key sequences...")
            conn.execute("SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));")
            conn.execute("SELECT setval('roles_id_seq', (SELECT MAX(id) FROM roles));")
            conn.execute("SELECT setval('auctions_id_seq', (SELECT MAX(id) FROM auctions));")
            conn.execute("SELECT setval('bids_id_seq', (SELECT MAX(id) FROM bids));")
            
            print("Database seeding completed successfully.")

        except Exception as e:
            session.rollback()
            print(f"Error seeding database: {e}")
            raise
        finally:
            session.close()
            request_scope.exit()

if __name__ == "__main__":
    seed_db()

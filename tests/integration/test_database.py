import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, UserDB
from main import app
from database import get_db
from dotenv import load_dotenv

load_dotenv()


class TestUserAPIIntegration:
    @pytest.fixture(scope="class")
    def test_engine(self):
        """Create test database engine using TEST_DATABASE_URL"""
        test_db_url = os.getenv("TEST_DATABASE_URL")
        if not test_db_url:
            pytest.skip("TEST_DATABASE_URL not configured in .env file")
        
        engine = create_engine(test_db_url)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        yield engine
        
        # Cleanup: Drop all tables after tests
        Base.metadata.drop_all(bind=engine)
        engine.dispose()

    @pytest.fixture(scope="function")
    def test_session(self, test_engine):
        """Create a test database session"""
        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        session = TestSessionLocal()
        
        yield session
        
        # Cleanup: Rollback any uncommitted changes and close session
        session.rollback()
        session.close()

    @pytest.fixture(scope="function")
    def test_client(self, test_session):
        """Create test client with database dependency override"""
        def override_get_db():
            try:
                yield test_session
            finally:
                pass
        
        app.dependency_overrides[get_db] = override_get_db
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    @pytest.fixture(autouse=True)
    def clean_database(self, test_session):
        """Clean all tables before each test"""
        test_session.query(UserDB).delete()
        test_session.commit()

    def test_create_user_api_stores_in_database(self, test_client, test_session):
        """Test that POST /api/users creates user in database"""
        user_data = {
            "name": "John Doe",
            "email": "john@example.com"
        }
        
        # Call API to create user
        response = test_client.post("/api/users", json=user_data)
        
        # Verify API response
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["name"] == "John Doe"
        assert response_data["email"] == "john@example.com"
        assert "id" in response_data
        assert "created_at" in response_data
        
        # Verify user was actually stored in database
        db_user = test_session.query(UserDB).filter(UserDB.email == "john@example.com").first()
        assert db_user is not None
        assert db_user.name == "John Doe"
        assert db_user.email == "john@example.com"
        assert db_user.id == response_data["id"]

    def test_get_users_api_reads_from_database(self, test_client, test_session):
        """Test that GET /api/users reads users from database"""
        # Create users directly in database
        users = [
            UserDB(name="Alice Smith", email="alice@example.com"),
            UserDB(name="Bob Johnson", email="bob@example.com")
        ]
        test_session.add_all(users)
        test_session.commit()
        
        # Call API to get users
        response = test_client.get("/api/users")
        
        # Verify API response
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 2
        
        emails = [user["email"] for user in response_data]
        assert "alice@example.com" in emails
        assert "bob@example.com" in emails

    def test_get_user_by_id_api_reads_from_database(self, test_client, test_session):
        """Test that GET /api/users/{id} reads specific user from database"""
        # Create user in database
        db_user = UserDB(name="Jane Doe", email="jane@example.com")
        test_session.add(db_user)
        test_session.commit()
        test_session.refresh(db_user)
        
        # Call API to get specific user
        response = test_client.get(f"/api/users/{db_user.id}")
        
        # Verify API response
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["name"] == "Jane Doe"
        assert response_data["email"] == "jane@example.com"
        assert response_data["id"] == db_user.id

    def test_update_user_api_updates_database(self, test_client, test_session):
        """Test that PUT /api/users/{id} updates user in database"""
        # Create user in database
        db_user = UserDB(name="Old Name", email="old@example.com")
        test_session.add(db_user)
        test_session.commit()
        test_session.refresh(db_user)
        
        # Call API to update user
        update_data = {
            "name": "New Name",
            "email": "new@example.com"
        }
        response = test_client.put(f"/api/users/{db_user.id}", json=update_data)
        
        # Verify API response
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["name"] == "New Name"
        assert response_data["email"] == "new@example.com"
        
        # Verify user was actually updated in database
        test_session.refresh(db_user)
        assert db_user.name == "New Name"
        assert db_user.email == "new@example.com"
        assert db_user.updated_at is not None

    def test_delete_user_api_removes_from_database(self, test_client, test_session):
        """Test that DELETE /api/users/{id} removes user from database"""
        # Create user in database
        db_user = UserDB(name="To Delete", email="delete@example.com")
        test_session.add(db_user)
        test_session.commit()
        user_id = db_user.id
        
        # Call API to delete user
        response = test_client.delete(f"/api/users/{user_id}")
        
        # Verify API response
        assert response.status_code == 200
        assert response.json()["message"] == "User deleted successfully"
        
        # Verify user was actually removed from database
        deleted_user = test_session.query(UserDB).filter(UserDB.id == user_id).first()
        assert deleted_user is None

    def test_create_user_duplicate_email_validation(self, test_client, test_session):
        """Test that API enforces email uniqueness constraint"""
        # Create first user via API
        user_data = {
            "name": "First User",
            "email": "duplicate@example.com"
        }
        response1 = test_client.post("/api/users", json=user_data)
        assert response1.status_code == 200
        
        # Try to create second user with same email
        user_data2 = {
            "name": "Second User",
            "email": "duplicate@example.com"
        }
        response2 = test_client.post("/api/users", json=user_data2)
        
        # Verify API rejects duplicate email
        assert response2.status_code == 400
        assert "Email already registered" in response2.json()["detail"]
        
        # Verify only one user exists in database
        users_count = test_session.query(UserDB).filter(UserDB.email == "duplicate@example.com").count()
        assert users_count == 1

    def test_pagination_with_database(self, test_client, test_session):
        """Test that API pagination works with database queries"""
        # Create multiple users in database
        users = [
            UserDB(name=f"User {i}", email=f"user{i}@example.com")
            for i in range(5)
        ]
        test_session.add_all(users)
        test_session.commit()
        
        # Test pagination via API
        response1 = test_client.get("/api/users?skip=0&limit=2")
        response2 = test_client.get("/api/users?skip=2&limit=2")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        page1_data = response1.json()
        page2_data = response2.json()
        
        assert len(page1_data) == 2
        assert len(page2_data) == 2
        
        # Ensure different users on different pages
        page1_ids = [user["id"] for user in page1_data]
        page2_ids = [user["id"] for user in page2_data]
        assert not any(id in page2_ids for id in page1_ids)

    def test_user_not_found_scenarios(self, test_client, test_session):
        """Test API behavior when user doesn't exist in database"""
        # Try to get non-existent user
        response1 = test_client.get("/api/users/999")
        assert response1.status_code == 404
        assert "User not found" in response1.json()["detail"]
        
        # Try to update non-existent user
        response2 = test_client.put("/api/users/999", json={"name": "New Name"})
        assert response2.status_code == 404
        assert "User not found" in response2.json()["detail"]
        
        # Try to delete non-existent user
        response3 = test_client.delete("/api/users/999")
        assert response3.status_code == 404
        assert "User not found" in response3.json()["detail"]
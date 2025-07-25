import pytest
from pydantic import ValidationError
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from models import UserCreate, UserUpdate, UserResponse


class TestUserModels:
    def test_user_create_valid(self):
        user_data = {
            "name": "John Doe",
            "email": "john@example.com"
        }
        user = UserCreate(**user_data)
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
    
    def test_user_create_invalid_email(self):
        user_data = {
            "name": "John Doe",
            "email": "invalid-email"
        }
        with pytest.raises(ValidationError):
            UserCreate(**user_data)
    
    def test_user_create_missing_name(self):
        user_data = {
            "email": "john@example.com"
        }
        with pytest.raises(ValidationError):
            UserCreate(**user_data)
    
    def test_user_update_partial(self):
        user_update = UserUpdate(name="Jane Doe")
        assert user_update.name == "Jane Doe"
        assert user_update.email is None
    
    def test_user_update_empty(self):
        user_update = UserUpdate()
        assert user_update.name is None
        assert user_update.email is None
    
    def test_user_update_invalid_email(self):
        with pytest.raises(ValidationError):
            UserUpdate(email="invalid-email")
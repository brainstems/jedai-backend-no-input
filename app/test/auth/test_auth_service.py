import pytest
from unittest.mock import patch, MagicMock
import jwt
from datetime import datetime, timedelta, timezone
from app.api.auth.service import AuthService

# Mock environment variables
@pytest.fixture(autouse=True)
def setup_env_vars(monkeypatch):
    monkeypatch.setenv('SECRET_KEY', 'test_secret')
    monkeypatch.setenv('ACCESS_TOKEN_EXPIRE_MINUTES', '60')

# Test the generate_token method
def test_generate_token():
    wallet_address = "0x123"
    token = AuthService.generate_token(wallet_address)

    # Decode the token to verify the payload
    payload = jwt.decode(token, 'test_secret', algorithms=["HS256"])

    # Assertions
    assert payload['wallet_address'] == wallet_address
    assert 'exp' in payload

# Test the authenticate method with a valid wallet
@patch('app.api.auth.service.WalletService')
def test_authenticate(mock_wallet_service):
    mock_wallet = MagicMock()
    mock_wallet_service.return_value.get_wallet_by_address.return_value = mock_wallet

    wallet_address = "0x123"
    token = AuthService.authenticate(wallet_address)

    # Assertions
    assert token is not None

# Test the authenticate method with an invalid wallet
@patch('app.api.auth.service.WalletService')
def test_authenticate_invalid_wallet(mock_wallet_service):
    mock_wallet_service.return_value.get_wallet_by_address.return_value = None

    wallet_address = "0x456"
    token = AuthService.authenticate(wallet_address)

    # Assertions
    assert token is None

# Test the verify_token method with a valid token
def test_verify_token():
    wallet_address = "0x123"
    token = AuthService.generate_token(wallet_address)

    # Verify the token
    payload = AuthService.verify_token(token)

    # Assertions
    assert payload['wallet_address'] == wallet_address

# Test the verify_token method with an expired token
def test_verify_token_expired():
    wallet_address = "0x123"
    expired_token = jwt.encode(
        {'wallet_address': wallet_address, 'exp': datetime.now(timezone.utc) - timedelta(minutes=1)},
        'test_secret',
        algorithm="HS256"
    )

    # Attempt to verify the expired token and expect a ValueError
    with pytest.raises(ValueError, match="Token has expired"):
        AuthService.verify_token(expired_token)

# Test the verify_token method with an invalid token
def test_verify_token_invalid():
    invalid_token = "invalid.token.value"

    # Attempt to verify the invalid token and expect a ValueError
    with pytest.raises(ValueError, match="Invalid token"):
        AuthService.verify_token(invalid_token)

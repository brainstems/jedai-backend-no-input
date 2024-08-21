import asyncio
from unittest.mock import AsyncMock, patch
from aiohttp import ClientError
import pytest
from app.api.db.db import DatabaseOperations
from app.api.predictions.service import PredictionService


@patch.object(DatabaseOperations, '__init__', lambda self: None)
@pytest.mark.asyncio
async def test_get_daily_event():
        database_operations = DatabaseOperations()
        prediction_service = PredictionService()
        database_operations.get_daily_event = AsyncMock(return_value={
        'Items': [
            {
                'start_ts': '2022-02-15T17:00:00+00:00',
                'end_ts': '2022-02-15T19:00:00+00:00',
                'assistantPrompt': 'some-context',
                'contextPrompt': 'some-prompt',
                'team': 'some-team'
            }
        ]
        })
        expected_fields = [
            'end_ts',
            'contextPrompt',
            'assistantPrompt',
            'team',
            'start_ts'
        ]
        # Call the function and verify the result
        with patch.object(DatabaseOperations, 'get_daily_event', database_operations.get_daily_event):
            result = await prediction_service.get_daily_event()

        # Verify that the result is as expected
        for field in expected_fields:
            assert field in result, f"Field {field} is missing from the result"

@patch.object(PredictionService, '__init__', lambda self: None)
@patch.object(DatabaseOperations, '__init__', lambda self: None)
@pytest.mark.asyncio
async def test_get_daily_event_no_items():
    # Call the function and verify the result
    database_operations = DatabaseOperations()
    prediction_service = PredictionService()
    database_operations.get_daily_event = AsyncMock(return_value={
    'Items': []
    })
    with patch.object(DatabaseOperations, 'get_daily_event', database_operations.get_daily_event):
        result = await prediction_service.get_daily_event()
    # Verify that the result is as expected
    assert result is None

@patch.object(PredictionService, '__init__', lambda self: None)
@patch.object(DatabaseOperations, '__init__', lambda self: None)
@pytest.mark.asyncio
async def test_get_next_event():
    database_operations = DatabaseOperations()
    prediction_service = PredictionService()
    database_operations.get_next_event = AsyncMock(return_value={
        'Items': [
            {
                'start_ts': '2022-02-15T17:00:00+00:00',
                'end_ts': '2022-02-15T19:00:00+00:00',
                'assistantPrompt': 'some-context',
                'contextPrompt': 'some-prompt',
                'team': 'some-team'
            }
        ]
    })

    # Call the function and verify the result
    expected_fields = [
        'start_date',
        'team'
    ]
    
    # Patch the method to use the mock
    with patch.object(DatabaseOperations, 'get_next_event', database_operations.get_next_event):
        # Call the method
        result = await prediction_service.get_next_event()

    # Verify that the result is as expected
    for field in expected_fields:
        assert field in result, f"Field {field} is missing from the result"


@patch.object(PredictionService, '__init__', lambda self: None)
@patch.object(DatabaseOperations, '__init__', lambda self: None)
@pytest.mark.asyncio
async def test_available_to_predict_no_items():
    # Create a mock instance of PredictionService
    prediction_service = PredictionService()
    database_operations = DatabaseOperations() 
    # Setup mocks
    address = 'some-address'
    team = 'some-team'
    # Hardcode the value directly in the method
    prediction_service.get_daily_event = AsyncMock(return_value={'team': team})
    database_operations.available_to_predict = AsyncMock(return_value={'Items': []})

    # Patch the method to use the mock
    with patch.object(DatabaseOperations, 'available_to_predict', database_operations.available_to_predict):
        # Call the method
        result = await prediction_service.available_to_predict(address)

    # Assert the result
    assert result is True, "Expected True when no items are returned by the query"

@pytest.mark.asyncio
@patch.object(PredictionService, '__init__', lambda self: None)
@patch.object(DatabaseOperations, '__init__', lambda self: None)
async def test_available_to_predict_with_items():
    # Setup
    address = 'some-address'
    prediction_service = PredictionService()
    database_operations = DatabaseOperations() 
    team = 'some-team'
    # Hardcode the value directly in the method
    prediction_service.get_daily_event = AsyncMock(return_value={'team': team})
    database_operations.available_to_predict = AsyncMock(return_value={'Items': [{'address': address, 'team': 'Team A'}]})
    with patch.object(DatabaseOperations, 'available_to_predict', database_operations.available_to_predict):
        # Call the method
        result = await prediction_service.available_to_predict(address)
    # Assert the result
    assert result is False, "Expected False when items are returned by the query"

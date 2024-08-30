from typing import Union

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.utils import BaseController

from .service import PredictionService

router = APIRouter()

prediction_service = PredictionService()


class PredictionRequest(BaseModel):
    prediction: str
    address: str
    team: str


class PredictionController(BaseController):
    prediction_service = PredictionService()

    @staticmethod
    async def create_prediction(
        request: PredictionRequest,
    ) -> dict[str, dict]:
        """
        Create a new prediction and store it in the database.

        Parameters:
        request (PredictionRequest): The request body containing the prediction details, which include:
            - prediction (str): The prediction text.
            - address (str): The address associated with the prediction.

        Returns:
        dict: A dictionary containing either:
            - "result" (dict): If the prediction was successfully saved, it includes the saved prediction details.
            - "error" (str): If the prediction could not be saved due to an existing prediction
            for the same address and team.

        Raises:
        HTTPException:
            - 500 Internal Server Error: If there is an unhandled exception during the process.

        Notes:
        - The endpoint expects a POST request with a JSON body containing the `prediction` and `address`.
        - If an error occurs, the endpoint returns a 500 status code with a detailed error message.
        - API key authentication is currently commented out but could be added by uncommenting the `api_key` parameter
          and using the `get_api_key` dependency.
        """
        try:
            result = await PredictionController.prediction_service.save_prediction(
                request.prediction, request.address, request.team
            )
            if isinstance(result, dict):
                return {"result": result}
            else:
                return {"error": result}
        except Exception as e:
            PredictionController.handle_backend_error(e)

    @staticmethod
    async def get_daily_event() -> dict[str, dict[str, str | int] | None]:
        """
        Retrieve the daily event from the database.

        Returns:
        dict: A dictionary containing:
            - "result" (dict): The details of the daily event retrieved from the database.

        Raises:
        HTTPException:
            - 500 Internal Server Error: If there is an unhandled exception during the process.

        Notes:
        - The endpoint is a GET request and does not require any parameters in the request body.
        - If an error occurs, the endpoint returns a 500 status code with a detailed error message.
        - API key authentication is currently commented out but could be added by uncommenting the `api_key` parameter
          and using the `get_api_key` dependency.
        """
        try:
            result = await PredictionController.prediction_service.get_daily_event()
            return {"result": result}
        except Exception as e:
            PredictionController.handle_backend_error(e)

    @staticmethod
    async def available_to_predict(address: str) -> dict[str, bool]:
        """
        Check if a prediction is available for a given address.

        Parameters:
        address (str): The address for which to check prediction availability.

        Returns:
        dict: A dictionary containing:
            - "available" (bool): True if a prediction can be made for the provided address, False otherwise.

        Raises:
        HTTPException:
            - 500 Internal Server Error: If there is an unhandled exception during the process.

        Notes:
        - The endpoint is a GET request that requires an `address` query parameter.
        - If an error occurs, the endpoint returns a 500 status code with a detailed error message.
        - API key authentication is currently commented out but could be added by uncommenting the `api_key` parameter
          and using the `get_api_key` dependency.
        """
        try:
            available = (
                await PredictionController.prediction_service.available_to_predict(
                    address
                )
            )
            return {"available": available}
        except Exception as e:
            PredictionController.handle_backend_error(e)

    @staticmethod
    async def get_address_history(address: str) -> dict[str, list[dict[str, int]]]:
        """
        Retrieve the prediction history for a given address.

        Parameters:
        address (str): The address for which to retrieve the prediction history.

        Returns:
        dict: A dictionary containing:
            - "history" (list): A list of prediction records associated with the provided address.

        Raises:
        HTTPException:
            - 500 Internal Server Error: If there is an unhandled exception during the process.

        Notes:
        - The endpoint is a GET request that requires an `address` query parameter.
        - If an error occurs, the endpoint returns a 500 status code with a detailed error message.
        """
        try:
            history = await PredictionController.prediction_service.get_address_history(
                address
            )
            return {"history": history}
        except Exception as e:
            PredictionController.handle_backend_error(e)

    @staticmethod
    async def get_next_event() -> dict[str, dict[str, str] | None]:
        """
        Retrieve the next scheduled event.

        Returns:
        dict: A dictionary containing:
            - "result" (dict): Information about the next scheduled event.

        Raises:
        HTTPException:
            - 500 Internal Server Error: If there is an unhandled exception during the process.

        Notes:
        - The endpoint is a GET request that does not require any parameters.
        - If an error occurs, the endpoint returns a 500 status code with a detailed error message.
        """
        try:
            result = await PredictionController.prediction_service.get_next_event()
            return {"result": result}
        except Exception as e:
            PredictionController.handle_backend_error(e)

    @staticmethod
    async def get_next_event_for_address(address: str) -> dict:
        """
        Retrieve the next event prediction for the given address.

        Args:
        address (str): The address for which to retrieve the next event prediction.

        Returns:
        dict: A dictionary containing:
            - "team" (str): The team associated with the next event.

        Raises:
        HTTPException:
            - 500 Internal Server Error: If there is an unhandled exception during the process.

        Notes:
        - The endpoint is a GET request that requires an address parameter.
        - If an error occurs, the endpoint returns a 500 status code with a detailed error message.
        """
        try:
            result = await PredictionController.prediction_service.get_address_prediction_event(
                address
            )
            return {"team": result}
        except Exception as e:
            PredictionController.handle_backend_error(e)


# Defining routes using the static methods of the PredictionController
@router.post("/", response_model=Union[dict[str, dict[str, str]], dict[str, str]])
async def create_prediction(
    request: PredictionRequest,
    # api_key: str = Depends(get_api_key)
) -> dict[str, dict]:
    return await PredictionController.create_prediction(request)


@router.get("/daily", response_model=dict[str, str | int])
async def get_daily_event(
    # api_key: str = Depends(get_api_key)
) -> dict[str, dict[str, str | int] | None]:
    return await PredictionController.get_daily_event()


@router.get("/available", response_model=dict[str, bool])
async def available_to_predict(
    address: str,
    # api_key: str = Depends(get_api_key)
) -> dict[str, bool]:
    return await PredictionController.available_to_predict(address)


@router.get("/history", response_model=dict[str, str | int])
async def get_address_history(address: str) -> dict[str, list[dict[str, int]]]:
    return await PredictionController.get_address_history(address)


@router.get("/next", response_model=dict[str, str])
async def get_next_event(
    # api_key: str = Depends(get_api_key)
) -> dict[str, dict[str, str] | None]:
    return await PredictionController.get_next_event()


@router.get("/open", response_model=dict)
async def get_next_event_for_address(address: str):
    return await PredictionController.get_next_event_for_address(address)

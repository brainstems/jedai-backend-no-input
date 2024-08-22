from fastapi import APIRouter

router = APIRouter()

@router.get("/", response_model=dict)
async def health_check():
    """
    Check the health status of the application.

    Returns:
    dict: A dictionary containing:
        - "status" (str): A message indicating the application is running.

    Notes:
    - This endpoint can be used by monitoring tools to check if the application is up and running.
    """
    return {"status": "Application is running"}

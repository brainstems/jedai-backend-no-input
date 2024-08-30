from fastapi import HTTPException, status


class BaseController:
    @staticmethod
    def handle_backend_error(e: Exception):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backend service error: {str(e)}",
        )

    @staticmethod
    def handle_no_inference():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Inference service unavailable",
        )

    @staticmethod
    def handle_no_event(message: str = "No event available"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

    @staticmethod
    def handle_no_authentication():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed or resource not found",
        )

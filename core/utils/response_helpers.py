from core.utils.common_schemas import SuccessResponse


def success_response(data=None, message="Success", status_code=200):
    return SuccessResponse(
        data=data,
        message=message,
        status_code=status_code,
    )
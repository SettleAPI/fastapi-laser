from dataclasses import dataclass

from fastapi import status
from pydantic import BaseModel

from fastapi_laser.exception_ext import BasePackageError

import app.schemas.shared


@dataclass
class AppHttpException(BasePackageError):
    """Generic HTTP exception compatible specific app requirements."""

    def __post_init__(self, inner_exception, message):
        super().__post_init__(inner_exception, message)
        if not isinstance(self.response, BaseModel):
            self.response = app.schemas.shared.BaseEndpointResponse(
                error=app.schemas.shared.ErrorDetails(
                    name=type(self).__name__,
                    description=self.__doc__,
                    permanent_failure=app.schemas.shared.ErrorDetails.is_permanent_failure(self.status_code),
                )
            )


@dataclass
class NotFoundError(AppHttpException):
    """Resources not found"""

    status_code: int = status.HTTP_404_NOT_FOUND

from typing import Optional

from pydantic import BaseModel, Field

from app import app_config


class ErrorDetails(BaseModel):
    name: str  # "Invalid request header"
    description: Optional[str]  # "X-My-Lovely-Id is a required parameter."
    permanent_failure: bool
    provider_failure_reason: Optional[str]

    @staticmethod
    def is_permanent_failure(status_code: int) -> bool:
        return 400 <= status_code < 500


# TODO: provide the information below as headers for all endpoints
class ProviderFields(BaseModel):
    provider: str = app_config.provider_name
    provider_version: str = app_config.provider_version


class BaseEndpointResponse(BaseModel):
    provider_fields: ProviderFields = Field(default_factory=ProviderFields)
    error: Optional[ErrorDetails] = None

    class Config:
        use_enum_values = True

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
    PydanticBaseSettingsSource,
    JsonConfigSettingsSource
)
from typing import Tuple, Type

class Settings(BaseSettings):
    model_config = SettingsConfigDict(json_file=("config/config_global.json", "config/config_local.json"), json_encoding="utf-8")
    access_tokens: list[str]

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (JsonConfigSettingsSource(settings_cls),)

settings = Settings()
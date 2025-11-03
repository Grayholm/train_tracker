from typing import Type

from pydantic import BaseModel

from src.core.db import Base


class DataMapper:
    db_model: Type[Base]
    schema: Type[BaseModel]

    @classmethod
    def map_to_domain_entity(cls, data) -> BaseModel:
        return cls.schema.model_validate(data, from_attributes=True)

    @classmethod
    def map_to_persistence_entity(cls, data) -> Base:
        return cls.db_model(**data.model_dump(exclude_unset=True))

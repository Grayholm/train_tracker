import logging

from asyncpg import UniqueViolationError
from pydantic import BaseModel, ValidationError
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import NoResultFound, IntegrityError

from src.exceptions import ValidationServiceError, ObjectNotFoundException
from src.repositories.mappers.base import DataMapper


class BaseRepository:
    model = None
    mapper: DataMapper = None

    def __init__(self, session):
        self.session = session

    async def get_filtered(self, *filter, **filters):
        query = select(self.model).filter(*filter).filter_by(**filters)
        result = await self.session.execute(query)
        data = result.scalars().all()
        return [self.mapper.map_to_domain_entity(model) for model in data]

    async def get_all(self):
        return await self.get_filtered()

    async def get_one_or_none(self, **filter):
        query = select(self.model).filter_by(**filter)
        result = await self.session.execute(query)
        sth = result.scalar_one_or_none()

        if sth:
            return self.mapper.map_to_domain_entity(sth)

        return None

    async def get_one(self, **filter_by) -> BaseModel:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            model = result.scalar_one()
        except NoResultFound:
            raise ObjectNotFoundException
        return self.mapper.map_to_domain_entity(model)

    async def add(self, data: BaseModel):
        add_stmt = (
            insert(self.model).values(**data.model_dump(exclude_unset=True)).returning(self.model)
        )
        try:
            result = await self.session.execute(add_stmt)
            created_data = result.scalar_one_or_none()
        except IntegrityError as e:
            logging.exception(f"Ошибка добавления данных в БД, входные данные={data}")
            if isinstance(e.orig.__cause__, UniqueViolationError):
                raise ObjectNotFoundException
            else:
                logging.exception(f"Незнакомая ошибка, входные данные={data}")
                raise e
        created = self.mapper.map_to_domain_entity(created_data)

        return created

    async def add_bulk(self, data: list[BaseModel]):
        add_data_stmt = insert(self.model).values(
            [item.model_dump(exclude_unset=True) for item in data]
        )
        await self.session.execute(add_data_stmt)

    async def update(self, data, **filter):
        if isinstance(data, BaseModel):
            update_data = data.model_dump(exclude_unset=True)
        elif isinstance(data, dict):
            update_data = data
        else:
            raise TypeError("Data must be either Pydantic model or dictionary")

        update_stmt = (
            update(self.model).filter_by(**filter).values(**update_data).returning(self.model)
        )
        result = await self.session.execute(update_stmt)

        try:
            obj = result.scalar_one()
            edited = self.mapper.map_to_domain_entity(obj)
        except NoResultFound:
            raise ObjectNotFoundException
        except ValidationError:
            raise ValidationServiceError
        except IntegrityError:
            raise

        return edited

    async def delete(self, **filter):
        delete_stmt = delete(self.model)
        if filter:
            delete_stmt = delete_stmt.filter_by(**filter)

        result = await self.session.execute(delete_stmt)

        if filter and result.rowcount == 0:
            raise ObjectNotFoundException

        return True

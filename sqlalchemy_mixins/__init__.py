from __future__ import annotations

from typing import List, Optional

# low-level, tiny mixins. you will rarely want to use them in real world
from fastapi.encoders import jsonable_encoder
from starlette_core.database import Session

# low-level, tiny mixins. you will rarely want to use them in real world
#from .session import SessionMixin
from .inspection import InspectionMixin

# high-level mixins
from .activerecord import ActiveRecordMixin, ModelNotFoundError
from .smartquery import SmartQueryMixin, smart_query
from .eagerload import EagerLoadMixin, JOINED, SUBQUERY
from .repr import ReprMixin
from .serialize import SerializeMixin
from .timestamp import TimestampsMixin

from .utils import classproperty

# https://accent-starlette.github.io/starlette-core/database/
from starlette_core.database import Base as AccentBase
from sqlalchemy_paginator import Paginator

from pydantic import BaseModel


# all features combined to one mixin
class AllFeaturesMixin(ActiveRecordMixin, SmartQueryMixin, ReprMixin, SerializeMixin):
    """ add support for pydantic schema
    """
    __abstract__ = True
    __repr__ = ReprMixin.__repr__


    def update_from_schema(self, schema: BaseModel) -> Base:
        item_data = jsonable_encoder(self)
        update_data = schema.dict(skip_defaults=True)

        # no need to loop item_data, because schema here is trust worthy
        # for field in item_data:
        #     if field in update_data:
        #         setattr(self, field, update_data[field])

        for field in update_data:
            setattr(self, field, update_data[field])

        return self.save_return()

    @classmethod
    def init_from_schema(cls, schema: BaseModel) -> Base:
        """Create and persist a new record for the model
        :param kwargs: attributes for the record
        :return: the new model instance
        """
        return  cls(**schema.dict(skip_defaults=True))


    @classmethod
    def create_from_schema(cls, db, schema: BaseModel, additions=None, ) -> Base:
        if additions is None:
            return cls(**schema.dict(skip_defaults=True)).save_return(db)

        return cls(**schema.dict(skip_defaults=True), **additions).save_return(db)

    @classmethod
    def paginate(cls, db, per_page_limit, optional_count_query_set=None,
                 allow_empty_first_page=True, ):
        return Paginator(db.query,
                         per_page_limit, optional_count_query_set, allow_empty_first_page)

    @classmethod
    def get_multi(cls, db, skip=0, limit=100, ) -> List[Optional[Base]]:

        return db.query.offset(skip).limit(limit).all()

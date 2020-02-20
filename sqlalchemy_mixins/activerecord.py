from starlette_core.database import Session
from starlette_core.database import Base as AccentBase
from starlette.exceptions import HTTPException

from .utils import classproperty
from .inspection import InspectionMixin


class ModelNotFoundError(ValueError):
    pass


class ActiveRecordMixin(InspectionMixin):
    __abstract__ = True

    def __init__(self):
        super().__init__()
        self._session = None

    def db(self, db):
        """
        alternative way to use db session, instead of starlette_core
        """
        self._session = db

    @classmethod
    def _get_query(cls, db=None):
        return cls.query if db is None else db.query

    @classproperty
    def settable_attributes(cls):
        return cls.columns + cls.hybrid_properties + cls.settable_relations

    def fill(self, **kwargs):
        for name in kwargs.keys():
            if name in self.settable_attributes:
                setattr(self, name, kwargs[name])
            else:
                raise KeyError("Attribute '{}' doesn't exist".format(name))

        return self

    def save_return(self,db=None):
        """Saves the updated model to the current entity db.
        """
        if db is not None:
            self.db(db)

        self.save(self)
        return self

    def update(self, **kwargs):
        """Same as :meth:`fill` method but persists changes to database.
        """
        return self.fill(**kwargs).save_return()

    # def delete_flush(self):
    #     """Removes the model from the current entity session and mark for deletion.
    #     """
    #     session = Session()
    #     session.delete(self)
    #     session.flush()

    @classmethod
    def create(cls, db=None, **kwargs):
        """Create and persist a new record for the model
        :param kwargs: attributes for the record
        :return: the new model instance
        """
        return cls().fill(**kwargs).save_return(db)

    @classmethod
    def destroy(cls, db=None, *ids):
        """Delete the records with the given ids
        :type ids: list
        :param ids: primary key ids of records
        """
        session = Session()
        query = cls._get_query(db)

        try:
            for pk in ids:
                session.delete(query.get(pk))
            session.commit()
        except:
            session.rollback()
            raise

    @classmethod
    def all(cls, db=None):
        return cls._get_query(db).all()

    @classmethod
    def first(cls, db=None):
        return cls._get_query(db).first()

    @classmethod
    def find(cls, id_, db=None):
        """Find record by the id
        :param id_: the primary key
        """
        return cls._get_query(db).get(id_)

    @classmethod
    def find_or_fail(cls, id_, detail=None, db=None):
        # assume that query has custom get_or_fail method
        result = cls.find(id_, db)
        if not result:
            if detail is None:
                detail = "{} with id '{}' was not found".format(cls.__name__, id_)
            raise HTTPException(
                status_code=404,
                detail=detail
            )
        return result

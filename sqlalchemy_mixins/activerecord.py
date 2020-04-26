from starlette.exceptions import HTTPException
import sqlalchemy as sa
from sqlalchemy_utils import dependent_objects, get_referencing_foreign_keys

from .utils import classproperty
from .inspection import InspectionMixin


class ModelNotFoundError(ValueError):
    pass

class ActiveRecordMixin(InspectionMixin):
    __abstract__ = True
    _session = None

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     self._session = None


    def db(self, db):
        """
        alternative way to use db session, instead of starlette_core
        """
        self._session = db

    def delete(self) -> None:
        """ delete the current instance """

        db = self._session

        try:
            db.delete(self)
            db.commit()
        except:
            db.rollback()
            raise

    def can_be_deleted(self) -> bool:
        """
        Simple helper to check if the instance has entities
        that will prevent this from being deleted via a protected foreign key.

        origin
        repo: https://accent-starlette.github.io/starlette-core/database/
        file: starlette_core\database.py
        """

        deps = list(
            dependent_objects(
                self,
                (
                    fk
                    for fk in get_referencing_foreign_keys(self.__class__)
                    # On most databases RESTRICT is the default mode hence we
                    # check for None values also
                    if fk.ondelete == "RESTRICT" or fk.ondelete is None
                ),
            ).limit(1)
        )

        return not deps

    def refresh_from_db(self) -> None:
        """ Refresh the current instance from the database """

        sa.inspect(self).session.refresh(self)

    # todo cache?
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

    def save(self,db=None) -> None:
        """ save the current instance """

        if db is None:
            db = self._session
        else:
            self.db(db)

        try:
            db.add(self)
            db.commit()
            # todo
            db.refresh(self)
        except:
            db.rollback()
            raise

    def save_return(self,db=None):
        """Saves the updated model to the current entity db.
        """
        self.save(db)
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
    def create_multi(cls, db,multi):
        """Create and persist a new record for the model
        :param kwargs: attributes for the record
        :return: the new model instance
        """
        try:
            for one in multi:
                ins = cls().fill(**one)
                db.add(ins)
            db.commit()
        except:
            db.rollback()
            raise


    @classmethod
    def destroy(cls, db, *ids):
        """Delete the records with the given ids
        :type ids: list
        :param ids: primary key ids of records
        """
        query = db.query(cls)

        try:
            for pk in ids:
                db.delete(query.get(pk))
            db.commit()
        except:
            db.rollback()
            raise

    @classmethod
    def all(cls, db):
        return db.query(cls).all()

    @classmethod
    def first(cls, db):
        return db.query(cls).first()

    @classmethod
    def find(cls,db, id_,):
        """Find record by the id
        :param id_: the primary key
        """
        return db.query(cls).get(id_)

    @classmethod
    def find_or_fail(cls,db, id_, detail=None, ):
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

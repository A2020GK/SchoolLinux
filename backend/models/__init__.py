from ..config import config
from sqlmodel import SQLModel, create_engine, Session
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


engine = create_engine(config.database_url, echo=config.debug)

# == SQL & DB Utils ==

def init_db():
    """
    Initialize the database by creating all tables defined in the SQLModel models.
    """
    SQLModel.metadata.create_all(engine)
    
def get_session():
    """
    Gets a new database session. Reverts all of the changes if an error occurs.
    """
    
    session = Session(engine)
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

# == API Utils ==

class BaseSchema(BaseModel):
    """Base schema, converts snake_case to camelCase JSON keys"""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )


# == Models import ==

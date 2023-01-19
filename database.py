from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# database engine
engine = create_engine('sqlite:///examer.db', 
                        connect_args={"check_same_thread": False}, 
                        echo=True,
                        future=True)

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

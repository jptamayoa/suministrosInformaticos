from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

#creacion del engine
engine = create_engine("sqlite:///database/suministros_informaticos.db")

#creación de la session
Session = sessionmaker(bind=engine)
session = Session()

#Vinculación clases con bd
Base = declarative_base()
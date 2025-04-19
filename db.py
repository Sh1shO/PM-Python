from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base


DATABASE_URL = "postgresql://postgres:1234@localhost:5432/aaa"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Company(Base):
    __tablename__ = "company"
    id = Column(Integer, primary_key=True)
    name = Column(String(200))

class JobName(Base):
    __tablename__ = "jobname"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

class Document(Base):
    __tablename__ = "document"
    id = Column(Integer, primary_key=True)
    series = Column(String(10))
    number = Column(String(20))

class Address(Base):
    __tablename__ = "address"
    id = Column(Integer, primary_key=True)
    address = Column(String(200))

class Employee(Base):
    __tablename__ = "employee"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    last_name = Column(String(50))
    middlename = Column(String(50))
    document_id = Column(Integer, ForeignKey("document.id"))
    address_id = Column(Integer, ForeignKey("address.id"))
    company_id = Column(Integer, ForeignKey("company.id"))
    jobname_id = Column(Integer, ForeignKey("jobname.id"))
    phone = Column(String(50))
    email = Column(String(50))
    start_date = Column(Date)

    document = relationship("Document")
    address = relationship("Address")
    company = relationship("Company")
    jobname = relationship("JobName")

def get_session():
    return Session()

Base.metadata.create_all(engine)
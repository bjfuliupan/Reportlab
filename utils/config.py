

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

SERVER_IP = "192.168.13.12"

DB_BASE = declarative_base()
engine = create_engine(
    f"mysql+pymysql://sboxweb:Sbox123456xZ@{SERVER_IP}:3306/sbox_db?charset=utf8",
    max_overflow=0,  # 超过连接池大小外最多创建的连接
    pool_size=5,  # 连接池大小
    pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
    pool_recycle=-1  # 多久之后对线程池中的线程进行一次连接的回收（重置）
)

SessionFactory = sessionmaker(bind=engine)
metadata = MetaData(engine)

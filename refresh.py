from app import *
import os

os.remove("database.db")
db.create_all()
from src.database import SongDatabase
from src.recognize import record_and_recognize

db = SongDatabase.load("data/database.json")

record_and_recognize(db)
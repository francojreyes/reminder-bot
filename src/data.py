"""
Class to store data using an interface to the MongoDB Client
Prompts and lists will not persist, fuck em
"""
import os
from datetime import datetime, timezone

import dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from src.classes.reminder import Reminder


class MyMongoClient(MongoClient):
    """Custom interface for MongoDB database"""

    def __init__(self):
        dotenv.load_dotenv()
        super().__init__(
            os.getenv('MONGODB_URL'), server_api=ServerApi('1'), connect=False)
        self.db = self.reminderbot
    
    def ping(self):
        """Ping the database"""
        self.db.command('ping')

    def add_reminder(self, reminder: Reminder):
        """Add a reminder to the database"""
        self.db.reminders.insert_one(reminder.__dict__)

    def remove_reminder(self, reminder: Reminder):
        """Delete a reminder from the database"""
        self.db.reminders.delete_one(reminder.__dict__)

    def get_offset(self, guild_id: int):
        """Retrieve the UTC offset of the given guild"""
        guild = self.db.guilds.find_one({'_id': guild_id})
        if guild:
            return guild['offset']
        else:
            self.db.guilds.insert_one({
                '_id': guild_id,
                'offset': 0,
                'target': None
            })
            return 0
    
    def set_offset(self, guild_id: int, offset: int):
        """Update the UTC offset of the given guild"""
        guild = self.db.guilds.find_one_and_update(
            {'_id': guild_id}, {'$set': {'offset': offset}})
        if not guild:
            self.db.guilds.insert_one({
                '_id': guild_id,
                'offset': offset,
                'target': None
            })

    def get_target(self, guild_id: int):
        """Retrieve the target channel of the given guild"""
        guild = self.db.guilds.find_one({'_id': guild_id})
        if guild:
            return guild['target']
        else:
            self.db.guilds.insert_one({
                '_id': guild_id,
                'offset': 0,
                'target': None
            })
            return None
    
    def set_target(self, guild_id: int, target: int):
        """Update the target channel of the given guild"""
        guild = self.db.guilds.find_one_and_update(
            {'_id': guild_id}, {'$set': {'target': target}})
        if not guild:
            self.db.guilds.insert_one({
                '_id': guild_id,
                'offset': 0,
                'target': target
            })

    def guild_reminders(self, guild_id: int):
        """Returns a list of all reminders matching the given guild_id"""
        res = self.db.reminders.find({'guild_id': guild_id}, sort=[('time', 1)])
        return [Reminder.from_dict(x) for x in res]

    def current_reminders(self):
        """Generator that finds all Reminders this minute"""
        now = round(datetime.now(timezone.utc).timestamp() / 60) * 60
        # Take advantage of the fact that there should be no reminders lt now
        return self.db.reminders.find({'time': {'$lt': now + 60}})


data = MyMongoClient()

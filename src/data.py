"""
Class to store reminders data
Prompts and lists will not persist, fuck em

Stored in a dict of the form
{
    guild_id (int) : {
        'target_channel': int,
        'utc_offest': int,
        'reminders': [Reminder dicts]
    },
    ...
}
"""
import os
from datetime import datetime

import dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from src.classes.reminder import Reminder


class MyMongoClient():
    """Custom interface for MongoDB database"""

    def __init__(self):
        dotenv.load_dotenv()
        self.client = MongoClient(
            os.getenv('MONGODB_URL'), server_api=ServerApi('1'), connect=False)
        self.db = self.client.reminderbot
    
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

    def get_target(self, guild_id: int):
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
            return None

    def guild_reminders(self, guild_id: int):
        """Returns a list of all reminders matching the given guild_id"""
        res = self.db.reminders.find({'guild_id': guild_id}, sort=[('time', 1)])
        return [Reminder.from_dict(x) for x in res]

    def current_reminders(self):
        """Iterator that finds and deletes all Reminders this minute"""
        now = round(datetime.now().timestamp() / 60) * 60
        # Take advantage of the fact that there should be no reminders lt now
        res = self.db.reminders.find({'time': {'$lt': now + 60}})

        try:
            x = next(res)
        except StopIteration:
            return

        while True:
            self.db.reminders.delete_one({'_id': x['_id']})
            yield(Reminder.from_dict(x))
            try:
                x = next(res)
            except StopIteration:
                break


data = MyMongoClient()

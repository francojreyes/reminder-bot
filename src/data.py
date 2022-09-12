"""
Class to store data using an interface to the MongoDB Client
Prompts and lists will not persist, fuck em
"""
import os
from datetime import datetime, timezone

import dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

from src.models.reminder import Reminder


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

    def get_timezone(self, guild_id: int):
        """Retrieve the timezone of the given guild"""
        guild = self.db.guilds.find_one(
            {'_id': guild_id}, {'timezone': 1, '_id': 0})
        if not guild:
            self.db.guilds.insert_one({
                '_id': guild_id,
                'timezone': 'UTC',
                'target': None,
                'role': None
            })
            return 'UTC'

        return guild['timezone']

    def set_timezone(self, guild_id: int, timezone: str):
        """Update the timezone of the given guild"""
        guild = self.db.guilds.find_one_and_update(
            {'_id': guild_id}, {'$set': {'timezone': timezone}})
        if not guild:
            self.db.guilds.insert_one({
                '_id': guild_id,
                'timezone': timezone,
                'target': None,
                'role': None
            })

    def get_target(self, guild_id: int):
        """Retrieve the target channel of the given guild"""
        guild = self.db.guilds.find_one(
            {'_id': guild_id}, {'target': 1, '_id': 0})
        if not guild:
            self.db.guilds.insert_one({
                '_id': guild_id,
                'timezone': 'UTC',
                'target': None,
                'role': None
            })
            return None

        return guild['target']

    def set_target(self, guild_id: int, target: int):
        """Update the target channel of the given guild"""
        guild = self.db.guilds.find_one_and_update(
            {'_id': guild_id}, {'$set': {'target': target}})
        if not guild:
            self.db.guilds.insert_one({
                '_id': guild_id,
                'timezone': 'UTC',
                'target': target,
                'role': None
            })

    def get_role(self, guild_id: int):
        """Retrieve the manager role of the given guild"""
        guild = self.db.guilds.find_one(
            {'_id': guild_id}, {'role': 1, '_id': 0})
        if not guild:
            self.db.guilds.insert_one({
                '_id': guild_id,
                'timezone': 'UTC',
                'target': None,
                'role': None
            })
            return None

        return guild['role']

    def set_role(self, guild_id: int, role: int):
        """Update the manager role of the given guild"""
        guild = self.db.guilds.find_one_and_update(
            {'_id': guild_id}, {'$set': {'role': role}})
        if not guild:
            self.db.guilds.insert_one({
                '_id': guild_id,
                'timezone': 'UTC',
                'target': None,
                'role': role
            })

    def guild_reminders(self, guild_id: int):
        """Returns a list of all reminders matching the given guild_id"""
        res = self.db.reminders.find(
            {'guild_id': guild_id}, sort=[('time', 1)])
        return [Reminder.from_dict(rem) for rem in res]

    def current_reminders(self):
        """Generator that deletes returns all Reminders this minute"""
        now = datetime.now(timezone.utc).timestamp() // 60 * 60
        # Take advantage of the fact that there should be no reminders lt now
        cursor = self.db.reminders.find({'time': {'$lt': int(now) + 60}})

        try:
            curr = next(cursor)
        except StopIteration:
            return

        while True:
            print("Retrieved reminder:", curr)
            yield Reminder.from_dict(curr)
            self.db.reminders.delete_one({'_id': curr['_id']})
            try:
                curr = next(cursor)
            except StopIteration:
                break
    
    def all_guilds(self):
        """Return all guilds"""
        return self.db.guilds.find({})
    
    def remove_guild(self, guild_id: int):
        """Remove guild by ID and all related reminders"""
        self.db.guilds.delete_one({'_id': guild_id})
        self.db.reminders.delete_many({'guild_id': guild_id})


data = MyMongoClient()

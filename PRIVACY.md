# Who we are
Reminder Bot is maintained solely by Franco Reyes. You can contact me by email at [franco.javier.reyes@gmail.com](mailto:franco.javier.reyes@gmail.com), or via private message on Discord at **@marshdapro**.

# What data we collect
Reminder Bot collects the following data for each server:
- Server ID
- Timezone
- Output channel ID
- Reminder manager role ID

Reminder Bot collects the following data for each reminder:
- Reminder content
- Reminder time and repeat interval
- Author ID
- Origin server ID
- Origin channel ID

No data is collected from individual users of Reminder Bot.

# Why we collect this data
Your data is used to keep track of where and when each reminder should be sent, whom the reminder is for, what the reminder is about.

Timezone data is collected to allow users to set reminders in their preferred/local timezone.

# Who your data is shared with
Your data is stored in a secure MongoDB Atlas instance, so you are guarded by the [privacy policies](https://www.mongodb.com/legal/privacy) of MongoDB.

# Removing your data
All data for a given server, as well as all reminders associated with that server, are removed from the database if Reminder Bot is removed from the server or the server is deleted.

Reminders deleted with `/remove` are removed from the database instantly.

Otherwise, data can be removed on request. Please contact me if you wish to remove your data.

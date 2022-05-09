STATES = {
    "init": {
        "field": {
            "name": "Select a reminder type",
            "value": ":one: - on... (a certain date)\n:two: - in... (an amount of time from now)"
        },
        "options": ["1️⃣", "2️⃣"],
        "next_state": {
            "1️⃣": "date",
            "2️⃣": "in_amount"
        },
        "append": {
            "1️⃣": " on...",
            "2️⃣": " in..."
        }
    },
    "date": {
        "field": {
            "name": "Enter a date",
            "value": "Format: DD-MM-YYYY"
        },
        "options": [],
        "next_state": "time",
        "append": " {0} at..."
    },
    "time": {
        "field": {
            "name": "Enter a time",
            "value": "Format: HH:MM"
        },
        "options": [],
        "next_state": "repeat",
        "append": " {0}, repeating..."
    },
    "in_amount": {
        "field": {
            "name": "Enter an amount",
            "value": "Format: number"
        },
        "options": [],
        "next_state": "in_select",
        "append": " {0}..."
    },
    "in_select": {
        "field": {
            "name": "Select a time period",
            "value": ":one: - hours\n:two: - days\n:three: - weeks\n:four: - months"
        },
        "options": ["1️⃣", "2️⃣", "3️⃣", "4️⃣"],
        "next_state": "repeat",
        "append": {
            "1️⃣": " hours, repeating...",
            "2️⃣": " days, repeating...",
            "3️⃣": " weeks, repeating...",
            "4️⃣": " months, repeating..."
        }
    },
    "repeat": {
        "field": {
            "name": "Repeat this reminder?",
            "value": ":regional_indicator_y: - Yes, repeat every...\n:regional_indicator_n: - No, set reminder"
        },
        "options": ["🇾", "🇳"],
        "next_state": {
            "🇾": "repeat_amount",
            "🇳": "confirm"
        },
        "append": {
            "🇾": " every...",
            "🇳": " never."
        },
    },
    "repeat_amount": {
        "field": {
            "name": "Enter an amount",
            "value": "Format: number"
        },
        "options": [],
        "next_state": "repeat_select",
        "append": " {0}..."
    },
    "repeat_select": {
        "field": {
            "name": "Select a time period",
            "value": ":one: - hours\n:two: - days\n:three: - weeks\n:four: - months"
        },
        "options": ["1️⃣", "2️⃣", "3️⃣", "4️⃣"],
        "next_state": "confirm",
        "append": {
            "1️⃣": " hours.",
            "2️⃣": " days.",
            "3️⃣": " weeks.",
            "4️⃣": " months."
        }
    },
    "confirm": {
        "field": {
            "name": "Confirm setting this reminder",
            "value": ":white_check_mark: - Confirm"
        },
        "options": ["✅"],
        "next_state": None
    }
}
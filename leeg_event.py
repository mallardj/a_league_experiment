import datetime
import cassiopeia as cass
from openai import OpenAI

client = OpenAI()


class LeagueChatEvent:
    champion_pool = cass.get_champions("NA")

    def __init__(self, game_time, mode, username, champ_name, msg):
        if champ_name not in LeagueChatEvent.champion_pool:
            return
        minute, sec = game_time.split(":")
        self.time = datetime.time(minute=int(minute), second=int(sec))
        self.mode = mode if not (mode is None) else "[Team]"  # OneHotEncode
        self.username = username  # Part of identifier. Do not encode.
        self.champ_name = champ_name  # OneHotEncode
        self.msg = msg  # Embed.
        self.evaluation = self.consultOpenAI()

    def consultOpenAI(self):
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You perform sentiment analysis on chat dialogue from League of Legends. Where "
                            "-1.0 signifies negative, and 1.0 signifies positive, return a number within [-1.0, 1.0]."
                            "If it's a ping, subtract 0.1 from the total."},
                {"role": "user", "content": self.msg}
            ]
        )
        return sum([float(i.message.content) for i in completion.choices]) / len(completion.choices)

    def __repr__(self):
        return (f"""League Event:
Time: {self.time.__repr__()}
Mode: {self.mode}
Champion: {self.champ_name}
Message: {self.msg}
Evaluation: {self.evaluation}
""")

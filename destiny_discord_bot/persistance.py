from pathlib import Path

from peewee import SqliteDatabase, Model, CharField

db = SqliteDatabase(str(Path(__file__).parents[1] / 'users.db'))


class User(Model):
    name = CharField()
    discord_id = CharField()
    steam_id = CharField()
    discriminator = CharField()

    class Meta:
        database = db

    @property
    def uname(self):
        return f"{self.name}#{self.discriminator}"

    @classmethod
    def search_from_input(cls, name):
        parts = name.split('#')
        try:
            discriminator = parts[1].strip()
        except IndexError:
            discriminator = None

        parsed = parts[0].strip()
        if parsed.startswith('<@!') and parsed.endswith('>'):
            predicate = cls.discord_id == parsed[3:-1]
        else:
            predicate = cls.name ** parsed
        if discriminator:
            predicate &= cls.discriminator == discriminator

        return cls.select().where(predicate)


db.create_tables([User])

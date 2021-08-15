import os


class ConfigKeys:
    MONGO_HOST = "MONGO_HOST"
    MONGO_DB = "MONGO_DB"
    USER_USERNAME = "USER_USERNAME"
    USER_PASSWORD = "USER_PASSWORD"
    SECRET_KEY = "SECRET_KEY"
    ALGO = "ALGO"


MONGO_HOST = os.environ[ConfigKeys.MONGO_HOST] if ConfigKeys.MONGO_HOST in os.environ else "mongodb://root:example@localhost"
MONGO_DB = os.environ[ConfigKeys.MONGO_DB] if ConfigKeys.MONGO_DB in os.environ else "MyWork"
USER_USERNAME = os.environ[ConfigKeys.USER_USERNAME] if ConfigKeys.USER_USERNAME in os.environ else "kacper"
USER_PASSWORD = os.environ[ConfigKeys.USER_PASSWORD] if ConfigKeys.USER_PASSWORD in os.environ else "kacper"
SECRET_KEY = os.environ[ConfigKeys.SECRET_KEY] if ConfigKeys.SECRET_KEY in os.environ else "cfa0b64b4f2a74fd7889144b15fe5118eab17dcdf1d7f75d6db75fd7d8db3e1e"
ALGO = os.environ[ConfigKeys.ALGO] if ConfigKeys.ALGO in os.environ else "HS256"

from threading import Thread

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
from app.models import BankAccount, raise_saving_accounts


def init_raise():
    users = BankAccount.query.all()
    for user in users:
        t = Thread(target=raise_saving_accounts, args=(user.id,))
        t.start()


raise_thread = Thread(target=init_raise)
raise_thread.start()

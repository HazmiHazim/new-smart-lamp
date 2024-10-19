from flask import Flask

# Import file
from Logger import Logger
from Database import Database
from api.UserApi import UserApi
from api.LampApi import LampApi
from api.DeletedDatasApi import DeletedDatasApi


# Initialize flask app
app = Flask(__name__)

logging = Logger()
database = Database(logging)

user_api = UserApi(__name__, logging=logging, database=database)
lamp_api = LampApi(__name__, logging=logging, database=database)
deleted_data_api = DeletedDatasApi(__name__, logging=logging, database=database)

# Register blueprints
app.register_blueprint(user_api.blueprint)
app.register_blueprint(lamp_api.blueprint)
app.register_blueprint(deleted_data_api.blueprint)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
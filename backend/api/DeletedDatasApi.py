import base64
from bson import ObjectId
from flask import request, jsonify, Blueprint

class DeletedDatasApi:
    
    def __init__(self, name, logging, database) -> None:
        self.blueprint = Blueprint("deleted_data", name)
        self.register_route()
        self.database = database
        self.logging = logging
        
    def register_route(self):
        
        @self.blueprint.route("/api/retrieve_all_deleted_datas/<user_id>", methods=["GET"])
        def api_retrieve_all_deleted_data(user_id):
            if request.method != "GET":
                return jsonify({
                    "errorMsg": "Method Not Allowed",
                    "statusCode": 405 
                }), 405
                
            try:
                # Decode the user id
                decode_user_id = base64.urlsafe_b64decode(user_id).decode()
                object_user_id = ObjectId(decode_user_id)
                user_collection = self.database.database_connection("users")
                user = user_collection.find_one({ "_id": object_user_id })
                if not user:
                    return jsonify({
                        "errorMsg": "Invalid ID.",
                        "statusCode": 404
                    })
                    
                deleted_data_collection = self.database.database_connection("deleted_datas")
                deleted_data_list = list(deleted_data_collection.find({}))
                # Convert return Object id to string
                for deleted_data in deleted_data_list:
                    # Convert return Object id to string
                    deleted_data["_id"] = str(deleted_data["_id"])
                    # Convert object id to random string byte (after encoding it to bytes first)
                    deleted_data["_id"] = base64.urlsafe_b64encode(deleted_data["_id"].encode()).decode()
                    
                return jsonify({
                    "successMsg": "Retrieve successful.",
                    "data": deleted_data_list,
                    "statusCode": 200
                }), 200
            
            except Exception as ex:
                self.logging.log_debug(str(ex))
                return jsonify({
                    "errorMsg": str(ex),
                    "statusCode": 500
                }), 500
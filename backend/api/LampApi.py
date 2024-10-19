import qrcode
import base64
import re
import uuid
import os, yaml
from flask import request, jsonify, Blueprint
from datetime import datetime
from bson import ObjectId

class LampApi:
    
    def __init__(self, name, logging, database) -> None:
        self.blueprint = Blueprint("lamp", name)
        self.register_route()
        self.database = database
        self.logging = logging
        
        with open(os.path.join("PATH_TO_YAML_FILE", "paths.yaml"), "r") as file:
            content = yaml.safe_load(file)
        self.images_path = content["images"]["base"]
        
    def register_route(self):
        
        @self.blueprint.route("/api/create_lamp/<user_id>", methods=["POST"])
        def api_create_lamp(user_id):
            if request.method != "POST":
                return jsonify({
                    "errorMsg": "Method Not Allowed",
                    "statusCode": 405 
                }), 405
                
            if not user_id:
                return jsonify({
                    "errorMsg": "ID parameters is missing. Please provide one.",
                    "statusCode": 400
                })
                
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
                                    
                request_data = request.get_json()
                required_keys = [
                    "led",
                    "status",
                    "intensity",
                    "colour"
                ]
                
                # Store missing keys if user forgot to give
                missing_keys = [key for key in required_keys if key not in request_data]
                if missing_keys:
                    return jsonify({
                        "errorMsg":  "Bad Request - Missing Parameters",
                        "missingParameters": missing_keys,
                        "statusCode": 400
                    }), 400
                    
                led = request_data["led"]
                status = request_data["status"]
                intensity = request_data["intensity"]
                colour = request_data["colour"]
                
                # Regular expression to match hex colour code entered by user
                hex_pattern = re.compile(r"^#([a-f0-9]{6}|[a-f0-9]{3})$", re.IGNORECASE)
                
                # Check if the hex code entered by user is valid format
                if not hex_pattern.match(request_data["colour"]):
                    return jsonify({
                        "errorMsg": "Invalid hex code.",
                        "statusCode": 400
                    }), 400
                
                # Create a time created and updated
                created_at = datetime.now().isoformat()
                updated_at = datetime.now().isoformat()
                created_by = decode_user_id
                updated_by = decode_user_id
                
                # Create id for qr code
                qr_code_id = uuid.uuid4().hex
                # Generate qr code image
                qr_code_image_generator = qrcode.make(qr_code_id)
                image_filename = f"LampQR_{qr_code_id}.png"
                qr_image_path = os.path.join(self.images_path, image_filename)
                # Save image to desire path
                qr_code_image_generator.save(qr_image_path)
                
                lamp_collection = self.database.database_connection("lamps")
                # Check if led is exists
                lamp = lamp_collection.find_one({ "led": led }, { "_id": 0 })
                if lamp:
                    return jsonify({
                        "errorMsg": "LED has been registered. Please enter another number.",
                        "statusCode": 409
                    }), 409
                    
                lamp_collection.insert_one({
                    "led": led,
                    "status": status,
                    "intensity": intensity,
                    "colour": colour,
                    "qr_id": qr_code_id,
                    "qr_image_path": qr_image_path,
                    "created_by": created_by,
                    "updated_by": updated_by,
                    "created_at": created_at,
                    "updated_at": updated_at
                })
                
                return jsonify({
                    "successMsg": "Create successful.",
                    "statusCode": 200
                }), 200
                
            except Exception as ex:
                self.logging.log_debug(str(ex))
                return jsonify({
                    "errorMsg": str(ex),
                    "statusCode": 500
                }), 500
            
            
        @self.blueprint.route("/api/retrieve_all_lamps/<user_id>", methods=["GET"])
        def api_retrieve_all_lamps(user_id):
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
                    
                lamp_collection = self.database.database_connection("lamps")
                lamp_list = list(lamp_collection.find({}))
                # Convert return Object id to string
                for lamp in lamp_list:
                    # Convert return Object id to string
                    lamp["_id"] = str(lamp["_id"])
                    # Convert object id to random string byte (after encoding it to bytes first)
                    lamp["_id"] = base64.urlsafe_b64encode(lamp["_id"].encode()).decode()
                    
                return jsonify({
                    "successMsg": "Retrieve successful.",
                    "data": lamp_list,
                    "statusCode": 200
                }), 200
            
            except Exception as ex:
                self.logging.log_debug(str(ex))
                return jsonify({
                    "errorMsg": str(ex),
                    "statusCode": 500
                }), 500
                
                
                
                
        @self.blueprint.route("/api/retrieve_lamp/<user_id>/<lamp_id>", methods=["GET"])
        def api_retrieve_lamp(user_id, lamp_id):
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
                    
                # Decode the user id
                decode_lamp_id = base64.urlsafe_b64decode(lamp_id).decode()
                object_lamp_id = ObjectId(decode_lamp_id)
                lamp_collection = self.database.database_connection("lamps")
                lamp = lamp_collection.find_one({ "_id": object_lamp_id })
                
                if not lamp:
                    return jsonify({
                        "errorMsg": "Lamp not found.",
                        "statusCode": 404
                    }), 404
                
                # Convert return Object id to string
                lamp["_id"] = str(lamp["_id"])
                    
                return jsonify({
                    "successMsg": "Retrieve successful.",
                    "data": lamp,
                    "statusCode": 200
                }), 200
            
            except Exception as ex:
                self.logging.log_debug(str(ex))
                return jsonify({
                    "errorMsg": str(ex),
                    "statusCode": 500
                }), 500
                
                
                
        @self.blueprint.route("/api/update_lamp/<user_id>/<lamp_id>", methods=["PUT"])
        def api_update_lamp(user_id, lamp_id):
            if request.method != "PUT":
                return jsonify({
                    "errorMsg": "Method Not Allowed",
                    "statusCode": 405 
                }), 405
                
            if not lamp_id and not user_id:
                return jsonify({
                    "errorMsg": "ID parameters is missing. Please provide one.",
                    "statusCode": 400
                })
                
            try:
                # Decode the user id
                decode_user_id = base64.urlsafe_b64decode(user_id).decode()
                object_user_id = ObjectId(decode_user_id)
                user_collection = self.database.database_connection("users")
                # Find user in database
                user = user_collection.find_one({ "_id": object_user_id })
                if not user:
                    return jsonify({
                        "errorMsg": "Invalid ID.",
                        "statusCode": 404
                    })
                    
                # Decode the lamp id
                decode_lamp_id = base64.urlsafe_b64decode(lamp_id).decode()
                object_lamp_id = ObjectId(decode_lamp_id)
                lamp_collection = self.database.database_connection("lamps")
                # Find lamp in database
                lamp = lamp_collection.find_one({ "_id": object_lamp_id })
                
                if not lamp:
                    return jsonify({
                        "errorMsg": "Lamp not found.",
                        "statusCode": 404
                    }), 404
                    
                request_data = request.get_json()
                required_keys = [
                    "status",
                    "intensity",
                    "colour"
                ]
                
                # Check if any required field is missing
                if not any(key in request_data for key in required_keys):
                    return jsonify({
                        "errorMsg": "At least one required field is missing.",
                        "requiredFields": required_keys,
                        "statusCode": 400
                    }), 400
                    
                update_fields = {}  # Create a dictionary for dynamic update query
                
                if "status" in request_data:
                    update_fields["status"] = request_data["status"]
                
                if "intensity" in request_data:
                    update_fields["intensity"] = request_data["intensity"]
                    
                if "colour" in request_data:
                    # Regular expression to match hex colour code entered by user
                    hex_pattern = re.compile(r"^#([a-f0-9]{6}|[a-f0-9]{3})$", re.IGNORECASE)
                    
                    # Check if the hex code entered by user is valid format
                    if not hex_pattern.match(request_data["colour"]):
                        return jsonify({
                            "errorMsg": "Invalid hex code.",
                            "statusCode": 400
                        }), 400
                        
                    update_fields["colour"] = request_data["colour"]
                    
                updated_at = datetime.now().isoformat()
                updated_by = decode_user_id
                
                # add fields updated_at and updated_by
                update_fields["updated_at"] = updated_at
                update_fields["updated_by"] = updated_by
                                        
                lamp_collection.update_one(
                    { "_id": object_lamp_id },
                    { "$set": update_fields }
                )
                
                return jsonify({
                    "successMsg": "Update successful.",
                    "statusCode": 200
                }), 200
                
            except Exception as ex:
                self.logging.log_debug(str(ex))
                return jsonify({
                    "errorMsg": str(ex),
                    "statusCode": 500
                }), 500
                
                
        @self.blueprint.route("/api/delete_lamp/<user_id>/<lamp_id>", methods=["DELETE"])
        def api_delete_lamp(user_id, lamp_id):
            if request.method != "DELETE":
                return jsonify({
                    "errorMsg": "Method Not Allowed",
                    "statusCode": 405 
                }), 405
                
            try:
                # Decode the user id
                decode_user_id = base64.urlsafe_b64decode(user_id).decode()
                object_user_id = ObjectId(decode_user_id)
                user_collection = self.database.database_connection("users")
                # Find user in database
                user = user_collection.find_one({ "_id": object_user_id })
                if not user:
                    return jsonify({
                        "errorMsg": "Invalid ID.",
                        "statusCode": 404
                    })
                    
                # Decode the lamp id
                decode_lamp_id = base64.urlsafe_b64decode(lamp_id).decode()
                object_lamp_id = ObjectId(decode_lamp_id)
                lamp_collection = self.database.database_connection("lamps")
                # Find lamp in database
                lamp = lamp_collection.find_one({ "_id": object_lamp_id })
                
                if not lamp:
                    return jsonify({
                        "errorMsg": "Lamp not found.",
                        "statusCode": 404
                    }), 404
                    
                qr_image_path = lamp["qr_image_path"]
                # Check if the file exists before attempting to delete
                if os.path.exists(qr_image_path):
                    os.remove(qr_image_path)
                    
                deleted_collection = self.database.database_connection("deleted_datas")
                deleted_data = {}
                deleted_data["deleted_lamp_id"] = decode_lamp_id
                deleted_data["deleted_by"] = decode_user_id
                deleted_collection.insert_one(deleted_data)
                    
                lamp_collection.delete_one({ "_id": object_lamp_id })
                return jsonify({
                    "successMsg": "Deleted successful.",
                    "statusCode": 200
                }), 200
                
            except Exception as ex:
                self.logging.log_debug(str(ex))
                return jsonify({
                    "errorMsg": str(ex),
                    "statusCode": 500
                }), 500
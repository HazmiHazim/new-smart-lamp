import bcrypt
import re
import base64
from flask import request, jsonify, Blueprint

class UserApi:
    
    def __init__(self, name, logging, database) -> None:
        self.blueprint = Blueprint("user", name)
        self.register_route()
        self.database = database
        self.logging = logging
        
    def register_route(self):
        
        @self.blueprint.route("/api/register_user", methods=["POST"])
        def api_register_user():
            if request.method != "POST":
                return jsonify({
                    "errorMsg": "Method Not Allowed",
                    "statusCode": 405 
                }), 405
                
            try:
                request_data = request.get_json()
                required_keys = [
                    "email",
                    "full_name",
                    "username",
                    "phone",
                    "password",
                    "confirm_password"
                ]
                
                # Store missing keys if user forgot to give
                missing_keys = [key for key in required_keys if key not in request_data]
                if missing_keys:
                    return jsonify({
                        "errorMsg":  "Bad Request - Missing Parameters",
                        "missingParameters": missing_keys,
                        "statusCode": 400
                    }), 400
                    
                email = request_data["email"]
                full_name = request_data["full_name"]
                username = request_data["username"]
                phone = request_data["phone"]
                password = request_data["password"]
                confirm_password = request_data["confirm_password"]
                
                user_collection = self.database.database_connection("users")
                user = user_collection.find_one({ "email": email }, {"_id": 0})
                
                if user:
                    return jsonify({
                        "errorMsg": "Email already exists.",
                        "statusCode": 409
                    }), 409
                    
                # Check if confirm password is same as password
                if confirm_password != password:
                    return jsonify({
                        "errorMsg": "Confirm password is not matching with password.",
                        "statusCode": 400
                    }), 400
                
                # Check if password is less than 9 character then return
                if len(password) < 9:
                    return jsonify({
                        "errorMsg": "Password must be at least 9 characters long.",
                        "statusCode": 400
                    }), 400
                
                # Check for at least one uppercase letter
                if not any(letter.isupper() for letter in password):
                    return jsonify({
                        "errorMsg": "Password must contain at least one uppercase letter.",
                        "statusCode": 400
                    }), 400
                
                if not re.search(r'[\W_]', password):
                    return jsonify({
                        "errorMsg": "Password must contain at least one special character.",
                        "statusCode": 400
                    }), 400
                
                # Check for at least one number
                if not any(letter.isdigit() for letter in password):
                    return jsonify({
                        "errorMsg": "Password must contain at least one number.",
                        "statusCode": 400
                    }), 400
                    
                # converting password to array of bytes 
                passord_bytes = password.encode("utf-8")
                
                # Hash password with salt
                # The '12' is the number that dictates the 'slowness'
                hash_password = bcrypt.hashpw(passord_bytes, bcrypt.gensalt(12))
                # decode the hash to prevent is encoded twice
                decoded_hash_password = hash_password.decode("utf-8")
                
                user_collection.insert_one({
                    "email": email,
                    "full_name": full_name,
                    "username": username,
                    "phone": phone,
                    "password": str(decoded_hash_password)
                })
                               
                return jsonify({
                    "successMsg": "Register successful.",
                    "statusCode": 200
                    }), 200
                
            except Exception as ex:
                self.logging.log_debug(str(ex))
                return jsonify({
                    "errorMsg": str(ex),
                    "statusCode": 500
                }), 500
                
                
                
            
        @self.blueprint.route("/api/authenticate_user", methods=["POST"])
        def api_authenticate_user():
            if request.method != "POST":
                return jsonify({
                    "errorMsg": "Method Not Allowed",
                    "statusCode": 405 
                }), 405
                
            try:
                auth_data = request.get_json()
                required_keys = [
                    "email",
                    "password"
                ]
                
                # Store missing keys if user forgot to give
                missing_keys = [key for key in required_keys if key not in auth_data]
                if missing_keys:
                    return jsonify({
                        "errorMsg":  "Bad Request - Missing Parameters",
                        "missingParameters": missing_keys,
                        "statusCode": 400
                    }), 400
                
                email = auth_data["email"]
                password = auth_data["password"]
                
                user_collection = self.database.database_connection("users")
                user = user_collection.find_one({ "email": email })
                
                if not user:
                    return jsonify({
                        "errorMsg": "Email does not exists in the record.",
                        "statusCode": 404
                    }), 404
                    
                # Convert the object id to string so that it can be return
                user["_id"] = str(user["_id"])
                
                # Converting password to array of bytes 
                passord_bytes = password.encode("utf-8")
                
                # Get user password from mongodb and convert it to byte
                password_db = user["password"].encode("utf-8")
                
                # Checking password 
                correct_password = bcrypt.checkpw(passord_bytes, password_db)
                
                if user and not correct_password:                        
                    return jsonify({
                        "errorMsg": "Authentication Failed. Password is wrong.",
                        "statusCode": 401,
                    })
                    
                # Convert object id to random string byte (after encoding it to bytes first)
                user_id_converted = base64.urlsafe_b64encode(user["_id"].encode()).decode()
                    
                return jsonify({
                    "successMsg": "Authenticate successful.",
                    "userId": user_id_converted,
                    "statusCode": 200,
                })
                
                
            except Exception as ex:
                self.logging.log_debug(str(ex))
                return jsonify({
                    "errorMsg": str(ex),
                    "statusCode": 500
                }), 500
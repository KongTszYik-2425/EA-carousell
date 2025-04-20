from flask_jwt_extended import create_access_token, jwt_required,jwt_required, get_jwt_identity, verify_jwt_in_request,decode_token
from application.models import Customer

def decodeCustomer(current_user_id):
    user_data = None
    if current_user_id:
        decoded_token = decode_token(current_user_id)
        current_user_id = decoded_token['sub']
        if current_user_id:
            user = Customer.query.get(current_user_id)
            if user:
                user_data = {
                    'custID': user.custID,
                    'username': user.username
                }
    return user_data
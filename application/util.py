from flask_jwt_extended import create_access_token, jwt_required,jwt_required, get_jwt_identity, verify_jwt_in_request,decode_token
from application.models import Customer
from google.oauth2 import service_account
from google.cloud import exceptions, storage
import uuid
import os


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

def upload_file_to_bucket(files: str)->tuple:
    key_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'service_account_key.json'))
    credentials = service_account.Credentials.from_service_account_file(key_file_path)
    bucket_name = 'ktybucket2425'
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    is_first = True 
    avatarUrl= ''
    image_paths = ''
    for file in files:
        if file:
            # 生成唯一的文件名
            unique_id = uuid.uuid4()
            image_name = f'image_{unique_id}.jpg'
            blob = bucket.blob(image_name)
            blob.upload_from_file(file)
            # 获取上传后的图片路径
            image_path = f'https://storage.googleapis.com/{bucket_name}/{image_name}'
            if is_first:
                avatarUrl = image_path
                is_first = False
            else:
                image_paths += image_path + ';'
    return (avatarUrl,image_paths)        
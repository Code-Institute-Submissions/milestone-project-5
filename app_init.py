from flask import Flask
from flask_login import LoginManager
import os
import boto3, botocore
# from e-commerce lesson
if os.path.exists('env.py'):
    import env

app = Flask(__name__)
login_manager = LoginManager()


S3_BUCKET= "paddywc-recipewiki-imgs"
# http://zabana.me/notes/upload-files-amazon-s3-flask.html
S3_KEY=os.environ.get("S3_ACCESS_KEY")
S3_SECRET = os.environ.get("S3_SECRET_ACCESS_KEY")
S3_LOCATION= 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)
s3 = boto3.client(
   "s3",
   aws_access_key_id=S3_KEY,
   aws_secret_access_key=S3_SECRET
)
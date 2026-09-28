
from datetime import datetime, timedelta,timezone
import jwt
from app.core.config import JWT_SECRET_KEY , JWT_ALGORITHM , JWT_ACCESS_TOKEN_EXPIRE_MINUTES
def create_access_token(data: dict)->str: # JWT Payload created
    to_encode = data.copy() # payload
    expire=datetime.now(timezone.utc)+timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire # adding to payload
    # creation of JWT Setup and secrete key is used to create signature not for creating jwt and secret key stays in server later signature will verify it.
    encode_jwt=jwt.encode(to_encode,key=JWT_SECRET_KEY,algorithm=JWT_ALGORITHM) #create jwt token using payload
    return encode_jwt


    
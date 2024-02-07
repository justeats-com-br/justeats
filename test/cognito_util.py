import base64
import hashlib
import hmac

import boto3

from src.infrastructure.common.config import get_key


class CognitoUtil(object):
    def __init__(self, user_pool_id=None, user_pool_client_id=None):
        self.cognito_client = boto3.client('cognito-idp',
                                           region_name=get_key('AWS_REGION'),
                                           aws_access_key_id=get_key('AWS_ACCESS_KEY_ID'),
                                           aws_secret_access_key=get_key('AWS_SECRET_ACCESS_KEY'),
                                           aws_session_token=get_key('AWS_SESSION_TOKEN'))
        self.user_pool_id = user_pool_id or get_key('cognito_user_pool_id')
        self.user_pool_client_id = user_pool_client_id or get_key('cognito_client_id')

    def create_user(self, email, password):
        self.cognito_client.admin_create_user(
            UserPoolId=self.user_pool_id,
            Username=email,
            TemporaryPassword=password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                }
            ],
            DesiredDeliveryMediums=['EMAIL'],
            MessageAction='SUPPRESS'
        )

    def create_confirmed_user(self, email, password):
        temp_password = 'temp12345678'
        self.create_user(email, temp_password)
        login_result = self._do_login(email, temp_password)
        session = login_result['Session']

        result = self.cognito_client.respond_to_auth_challenge(
            ClientId=self.user_pool_client_id,
            ChallengeName='NEW_PASSWORD_REQUIRED',
            ChallengeResponses={
                'NEW_PASSWORD': password,
                'USERNAME': email,
                'SECRET_HASH': self._get_secret_hash(email)
            },
            Session=session
        )
        return result['AuthenticationResult']['AccessToken'], result['AuthenticationResult']['RefreshToken']

    def _do_login(self, email, password):
        return self.cognito_client.admin_initiate_auth(
            UserPoolId=self.user_pool_id,
            ClientId=self.user_pool_client_id,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password,
                'SECRET_HASH': self._get_secret_hash(email)
            }
        )

    def _get_secret_hash(self, email):
        message = email + self.user_pool_client_id
        dig = hmac.new(get_key('cognito_client_secret').encode('utf8'), msg=str(message).encode('utf8'),
                       digestmod=hashlib.sha256).digest()
        return base64.b64encode(dig).decode()

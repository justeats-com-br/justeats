import base64
import hashlib
import hmac
from gettext import gettext
from typing import List, Tuple
from uuid import uuid4

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ParamValidationError

from src.infrastructure.common.config import get_key, ENVIRONMENT
from src.infrastructure.common.either import Right, Left, Either
from src.infrastructure.common.message import Message, MessageCategory


class AuthService:
    def __init__(self, cognito_client: BaseClient = None):
        self.cognito_client = cognito_client or boto3.client('cognito-idp',
                                                             region_name=get_key('AWS_REGION'),
                                                             aws_access_key_id=get_key('AWS_ACCESS_KEY_ID'),
                                                             aws_secret_access_key=get_key('AWS_SECRET_ACCESS_KEY'),
                                                             aws_session_token=get_key('AWS_SESSION_TOKEN'))

    def sign_up(self, email, password):
        temp_password = self._invite_user(email)
        result = self._first_login(email, temp_password, password)
        if result.is_right():
            token = result.right()[0]
            refresh_token = result.right()[1]
            return Right((token, refresh_token))
        else:
            return result

    def login(self, email, password):
        login_result = self._do_login(email, password)

        if login_result.is_right():
            requested_challenge = login_result.right().get('ChallengeName')
            if not requested_challenge:
                token = login_result.right()['AuthenticationResult']['AccessToken']
                refresh_token = login_result.right()['AuthenticationResult']['RefreshToken']
                return Right((token, refresh_token))
            elif requested_challenge == 'NEW_PASSWORD_REQUIRED':
                return Left([Message(
                    category=MessageCategory.VALIDATION,
                    target='password',
                    message=gettext('First login required'),
                    key='first_login_required'
                )])
            else:
                raise Exception('Unknown requested challenge on login: {}'.format(requested_challenge))
        else:
            return login_result

    def load_username_by_token(self, token):
        try:
            result = self.cognito_client.get_user(
                AccessToken=token
            )
            return Right(
                next(attribute['Value'] for attribute in result['UserAttributes'] if attribute['Name'] == 'email'))
        except Exception as e:
            if e.response['Error']['Code'] == 'NotAuthorizedException':
                return Left([Message(
                    category=MessageCategory.VALIDATION,
                    target='access_token',
                    message=gettext('Invalid token'),
                    key='invalid_token'
                )])
            else:
                raise e

    def refresh_token(self, email: str, refresh_token: str) -> Either[List[Message], Tuple[str, str]]:
        try:
            username = self._load_username_by_email(email)
            refresh_result = self.cognito_client.admin_initiate_auth(UserPoolId=get_key('cognito_user_pool_id'),
                                                                     ClientId=get_key('cognito_client_id'),
                                                                     AuthFlow='REFRESH_TOKEN_AUTH',
                                                                     AuthParameters={'REFRESH_TOKEN': refresh_token,
                                                                                     })
            token = refresh_result['AuthenticationResult']['AccessToken']
            return Right((token, refresh_token))
        except Exception as e:
            if e.response['Error']['Code'] == 'NotAuthorizedException':
                return Left([Message(
                    category=MessageCategory.VALIDATION,
                    target='refresh_token',
                    message=gettext('Invalid token'),
                    key='invalid_token'
                )])
            else:
                raise e

    def send_password_recovery(self, email):
        try:
            self.cognito_client.forgot_password(
                ClientId=get_key('cognito_client_id'),
                Username=email
            )

            return Right(email)
        except Exception as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UserNotFoundException':
                return Left([Message(
                    category=MessageCategory.VALIDATION,
                    target='email',
                    message=gettext('User not found'),
                    key='user_not_found'
                )])
            elif error_code == 'LimitExceededException':
                return Left([Message(
                    category=MessageCategory.VALIDATION,
                    target='email',
                    message=gettext('Too many requests, try again later'),
                    key='too_many_requests'
                )])
            else:
                raise e

    def reset_password(self, email, verification_code, new_password):
        try:
            self.cognito_client.confirm_forgot_password(
                ClientId=get_key('cognito_client_id'),
                Username=email,
                ConfirmationCode=verification_code,
                Password=new_password,
            )
            return Right(email)
        except ParamValidationError:
            return Left([Message(
                category=MessageCategory.VALIDATION,
                target='new_password',
                message=gettext('Insufficient password strength'),
                key='insufficient_password_strength'
            )])
        except Exception as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ExpiredCodeException' or error_code == 'CodeMismatchException':
                return Left([Message(
                    category=MessageCategory.VALIDATION,
                    target='verification_code',
                    message=gettext('Invalid recovery code'),
                    key='invalid_token'
                )])
            else:
                raise e

    def _load_username_by_email(self, email):
        result = self.cognito_client.list_users(
            UserPoolId=get_key('cognito_user_pool_id'),
            Limit=1,
            Filter='email="{}"'.format(email)
        )

        if len(result['Users']) == 1:
            return result['Users'][0]['Username']

    def _invite_user(self, email):
        temp_password = str(uuid4())

        self.cognito_client.admin_create_user(
            UserPoolId=get_key('cognito_user_pool_id'),
            Username=email,
            TemporaryPassword=temp_password,
            MessageAction='SUPPRESS',
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                },
                {
                    'Name': 'email_verified',
                    'Value': 'true'
                }
            ],
            DesiredDeliveryMediums=['EMAIL']
        )

        return temp_password

    def _first_login(self, email, temporary_password, new_password):
        login_result = self._do_login(email, temporary_password)

        if login_result.is_right():
            if login_result.right()['ChallengeName'] == 'NEW_PASSWORD_REQUIRED':
                session = login_result.right()['Session']
                tokens = self._do_new_password_challenge(email, new_password, session)
                return Right(tokens)
            else:
                raise Exception('Invalid response from Cognito %s' % login_result)
        else:
            return login_result

    def _do_new_password_challenge(self, email, new_password, session):
        try:
            if ENVIRONMENT != 'TEST':
                new_password_result = self.cognito_client.admin_respond_to_auth_challenge(
                    UserPoolId=get_key('cognito_user_pool_id'),
                    ClientId=get_key('cognito_client_id'),
                    ChallengeName='NEW_PASSWORD_REQUIRED',
                    ChallengeResponses={
                        'NEW_PASSWORD': new_password,
                        'USERNAME': email
                    },
                    Session=session
                )

                return (new_password_result['AuthenticationResult']['AccessToken'],
                        new_password_result['AuthenticationResult']['RefreshToken'])
            else:
                result = self.cognito_client.respond_to_auth_challenge(
                    ClientId=get_key('cognito_client_id'),
                    ChallengeName='NEW_PASSWORD_REQUIRED',
                    ChallengeResponses={
                        'NEW_PASSWORD': new_password,
                        'USERNAME': email,
                        'SECRET_HASH': self._get_secret_hash(email)
                    },
                    Session=session
                )
                return result['AuthenticationResult']['AccessToken'], result['AuthenticationResult']['RefreshToken']
        except Exception as e:
            if e.response['Error']['Code'] == 'InvalidPasswordException':
                return Left([Message(
                    category=MessageCategory.VALIDATION,
                    target='password',
                    message=gettext('Invalid password'),
                    key='invalid_password'
                )])
            else:
                raise e

    def _do_login(self, email, password):
        try:
            return Right(self.cognito_client.admin_initiate_auth(UserPoolId=get_key('cognito_user_pool_id'),
                                                                 ClientId=get_key('cognito_client_id'),
                                                                 AuthFlow='ADMIN_NO_SRP_AUTH',
                                                                 AuthParameters={'USERNAME': email,
                                                                                 'PASSWORD': password,
                                                                                 }))
        except Exception as e:
            if e.response['Error']['Code'] == 'NotAuthorizedException' or \
                    e.response['Error']['Code'] == 'UserNotFoundException':
                return Left([Message(
                    category=MessageCategory.VALIDATION,
                    target='credentials',
                    message=gettext('Wrong credentials'),
                    key='wrong_credentials'
                )])
            else:
                raise e

    def _get_secret_hash(self, email):
        message = email + get_key('cognito_client_id')
        dig = hmac.new(get_key('cognito_client_secret').encode('utf8'), msg=str(message).encode('utf8'),
                       digestmod=hashlib.sha256).digest()
        return base64.b64encode(dig).decode()

import re
from typing import List, Optional

from cerberus import Validator
from cerberus.errors import ErrorDefinition

from src.infrastructure.common.message import Message
from src.infrastructure.common.message_mapper import MessageMapper
from src.users.domain.model.user import User
from src.users.domain.model.user_repository import UserRepository


class UserValidations(Validator):
    def __init__(self, user_repository: UserRepository, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_repository = user_repository

    def _validate_invalid_email(self, constraint, field, value):
        if value:
            re_obj = re.compile('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
            if not re_obj.match(value):
                self._error(field, ErrorDefinition(0, 'invalid_email'))
                self.recent_error.constraint = None

    def _validate_unique_email(self, constraint, field, value):
        if value:
            found_user = self.user_repository.load_by_email(value)
            if found_user:
                self._error(field, ErrorDefinition(0, 'unique_email'))
                self.recent_error.constraint = None


class UserValidator:
    def __init__(self, user_repository: Optional[UserRepository] = None):
        self.user_repository = user_repository or UserRepository()

    def validate_new_user(self, user: User) -> List[Message]:
        validation_schema = {
            'email': {'required': True, 'empty': False, 'invalid_email': True, 'unique_email': True},
            'name': {'required': True, 'empty': False, 'maxlength': 100},
            'type': {'required': True},
        }
        validator = UserValidations(self.user_repository, validation_schema, allow_unknown=True)
        validator.validate({
            'email': user.email,
            'name': user.name,
            'type': user.type,
        })
        return MessageMapper.to_messages(validator._errors)

    def validate_update_user(self, user: User) -> List[Message]:
        validation_schema = {
            'email': {'required': True, 'empty': False, 'invalid_email': True},
            'name': {'required': True, 'empty': False, 'maxlength': 100},
            'type': {'required': True},
        }
        validator = UserValidations(self.user_repository, validation_schema, allow_unknown=True)
        validator.validate({
            'email': user.email,
            'name': user.name,
            'type': user.type,
        })
        return MessageMapper.to_messages(validator._errors)

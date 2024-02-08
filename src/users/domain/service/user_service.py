from typing import List, Tuple, Optional

from src.infrastructure.common.domain_event import EventType
from src.infrastructure.common.either import Either, Left, Right
from src.infrastructure.common.message import Message
from src.infrastructure.topic.domain_event_notifier import DomainEventNotifier
from src.users.domain.model.user import User
from src.users.domain.model.user_repository import UserRepository
from src.users.domain.model.user_validator import UserValidator
from src.users.domain.service.auth_service import AuthService


class UserService:
    def __init__(self, user_validator: Optional[UserValidator] = None,
                 user_repository: Optional[UserRepository] = None,
                 auth_service: Optional[AuthService] = None,
                 domain_event_notifier: Optional[DomainEventNotifier] = None):
        self.user_validator = user_validator or UserValidator()
        self.user_repository = user_repository or UserRepository()
        self.auth_service = auth_service or AuthService()
        self.domain_event_notifier = domain_event_notifier or DomainEventNotifier()

    def sign_up(self, user: User, password: str) -> Either[List[Message], Tuple[User, str, str]]:
        messages = self.user_validator.validate_new_user(user)
        if messages:
            return Left(messages)
        else:
            sign_up_result = self.auth_service.sign_up(user.email, password)
            if sign_up_result.is_right():
                self.user_repository.add(user)
                self.domain_event_notifier.notify_event(user.id, user, EventType.ADDED)
                token, refresh_token = sign_up_result.right()
                return Right((user, token, refresh_token))
            else:
                return sign_up_result

from typing import List

from cerberus.errors import ValidationError
from flask_babel import gettext

from src.infrastructure.common.message import MessageCategory, Message


class MessageMapper:
    @staticmethod
    def to_messages(errors: List[ValidationError]) -> List[Message]:
        messages = []
        for error in errors:
            messages.extend(MessageMapper.to_message(error))
        return messages

    @staticmethod
    def to_message(error: ValidationError) -> List[Message]:
        return MessageMapper._to_message(error, [])

    @staticmethod
    def _to_message(error: ValidationError, acc: List[Message]) -> List[Message]:
        if error.child_errors:
            for child_error in error.child_errors:
                acc.extend(MessageMapper._to_message(child_error, acc))
            return acc
        else:
            if error.constraint:
                args = error.constraint if isinstance(error.constraint, List) else [error.constraint]
            else:
                args = None

            key = error.rule
            return [Message(category=MessageCategory.VALIDATION,
                            target='.'.join(error.document_path),
                            message=MessageMapper._to_message_text(key),
                            key=key,
                            args=args)]

    @staticmethod
    def _to_message_text(key: str) -> str:
        if key == 'empty':
            return gettext('Required field')
        elif key == 'nullable':
            return gettext('Required field')
        elif key == 'invalid_recipe':
            return gettext('Invalid recipe')
        elif key == 'allowed':
            return gettext('Invalid value')
        elif key == 'invalid_prompt_execution':
            return gettext('Invalid prompt execution')
        elif key == 'maxlength':
            return gettext('Maximum length exceeded')
        elif key == 'minlength':
            return gettext('Minimum length not reached')
        elif key == 'invalid_email':
            return gettext('Invalid email')
        elif key == 'unique_email':
            return gettext('Email already in use')
        elif key == 'invalid_document_number':
            return gettext('Invalid document number')
        elif key == 'unique_document_number':
            return gettext('Document number already in use')
        elif key == 'invalid_image_type':
            return gettext('Invalid image type')
        else:
            raise ValueError(f'Unknown key: {key}')

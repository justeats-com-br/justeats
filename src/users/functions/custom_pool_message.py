from gettext import gettext

from src.infrastructure.common.lambda_handler import LambdaHandler


class CustomPoolMessage(LambdaHandler):
    def handle(self, event, context):
        if event['triggerSource'] == 'CustomMessage_ForgotPassword':
            event['response']['emailSubject'] = gettext('Your password recovery code')
            event['response']['emailMessage'] = gettext('Hello, here is your recovery code: {####}.')
        return event


handle = CustomPoolMessage()

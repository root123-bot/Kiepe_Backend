import http.client
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
import os
import requests
from requests.exceptions import ConnectionError, HTTPError
import africastalking

username = "Paschal"
api_key = "atsk_7f62f931ac8d1d2985683207ba26cec63bfe02ad9ee235d7ed7dc52e780e513b5b05b5af"
sender = "BUFEE"


def sendOTP(phone_no, message):
    africastalking.initialize(username, api_key)

    sms = africastalking.SMS

    response = sms.send(message, [phone_no], sender)

    return response    


# Optionally providing an access token within a session if you have enabled push security
session = requests.Session()
session.headers.update(
    {
        "Authorization": f"Bearer {os.getenv('EXPO_TOKEN')}",
        "accept": "application/json",
        "accept-encoding": "gzip, deflate",
        "content-type": "application/json",
    }
)

# send notification to mobile app
# https://somehowitworked.dev/push-notifications-react-native-expo-django/
# https://stackoverflow.com/questions/71040572/how-can-i-schedule-expo-notifications-from-python
def sendNotification(title, body, token):
    message = {
        'to' :  token,
        'title' : title,
        'sound' : "default",
        'body' : body
    }
    return requests.post('https://exp.host/--/api/v2/push/send', json = message)


# The Expo push notification service
def send_push_message(token, message, extra=None):
    try:
        response = PushClient(session=session).publish(
            PushMessage(to=token,
                        body=message,
                        data=extra))
    except PushServerError as exc:
        # Encountered some likely formatting/validation error.
        rollbar.report_exc_info(
            extra_data={
                'token': token,
                'message': message,
                'extra': extra,
                'errors': exc.errors,
                'response_data': exc.response_data,
            })
        raise
    except (ConnectionError, HTTPError) as exc:
        # Encountered some Connection or HTTP error - retry a few times in
        # case it is transient.
        rollbar.report_exc_info(
            extra_data={'token': token, 'message': message, 'extra': extra})
        raise self.retry(exc=exc)

    try:
        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception
        # flows.
        response.validate_response()
    except DeviceNotRegisteredError:
        # Mark the push token as inactive
        from notifications.models import PushToken
        PushToken.objects.filter(token=token).update(active=False)
    except PushTicketError as exc:
        # Encountered some other per-notification error.
        rollbar.report_exc_info(
            extra_data={
                'token': token,
                'message': message,
                'extra': extra,
                'push_response': exc.push_response._asdict(),
            })
        raise self.retry(exc=exc)

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


def sendOTP(phone_no="+255623317196" , sms="Your OTP is 1234"):

    BASE_URL = "q984r.api.infobip.com"
    API_KEY = "App a3480056f1de0e51d92140f8f6fe1e09-84c08e58-5e12-403e-b349-2e46ffd1d29e"

    # SENDER = "Jipime"
    SENDER = "ConnectMoja"
    # SENDER = "AfyaTap"
    RECIPIENT = phone_no
    MESSAGE_TEXT = sms

    conn = http.client.HTTPSConnection(BASE_URL)

    payload1 = "{\"messages\":" \
            "[{\"from\":\"" + SENDER + "\"" \
            ",\"destinations\":" \
            "[{\"to\":\"" + RECIPIENT + "\"}]," \
            "\"text\":\"" + MESSAGE_TEXT + "\"}]}"

    headers = {
        'Authorization': API_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    conn.request("POST", "/sms/2/text/advanced", payload1, headers)

    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))


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

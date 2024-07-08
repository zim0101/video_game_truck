import os
from twilio.rest import Client
# from credentials import account_sid, auth_token

account_sid = "AC40d2d714b758276483490c907318fe7d"
auth_token = "a8c375144ea8718a7dc02bd542a6ade3"


def send_sms(message):
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=message,
        from_="+12568297375",
        to="+8801617308431",
    )

    print(message.sid)

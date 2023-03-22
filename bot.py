import os
import re
from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request, jsonify


# Load environment variables
from dotenv import load_dotenv
load_dotenv()
app = App(token=os.environ.get("SLACK_BOT_TOKEN"), signing_secret=os.environ.get("SLACK_SIGNING_SECRET"))


slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])


# Send the customized message to a channel
def send_message(channel_id, message):
    try:
        slack_client.chat_postMessage(channel=channel_id, text=message)
    except SlackApiError as e:
        print(f"Error: {e}")

def parse_event_parameters(text):
    pattern = r"customer:\s*(.*?)\s+environment:\s*(.*?)\s+datetime:\s*(.*?)+remarks:\s*(.*)"
    match = re.search(pattern, text, re.IGNORECASE)
    print('Match:')
    print(match)

    if match:
        customer = match.group(1)
        environment = match.group(2)
        datetime = match.group(3)
        remarks = match.group(4)
        return customer, environment, datetime, remarks

    return None

# Define the trigger word for your bot
trigger_word = "!deploy"
# Listen for app_mention events
@app.event("app_mention")
def handle_app_mentions(body, say):
    text = body["event"].get("text")
    user = body['event'].get('user')
    print('User: ' + user)
    print('Text: ' + text)
    
    if trigger_word in text:
        event_parameters = parse_event_parameters(text)
        if event_parameters:
            customer, environment, datetime, remarks = event_parameters
            message = "`[" + customer + "]`"
            if environment:
                message = message + " `[" + environment + "]`"
            message = message + " Deployment requested by <@" + user + ">.\n"
            if datetime:
                message = message + "It is planned for " + datetime + ".\n"
            print("DateTime: " + datetime)
            if remarks:
                message = message + "Additional remarks: " + remarks
            target_channel = "#deployments"
            print("Message: " + message)
            send_message(target_channel, message)
        else:
            say(f"Sorry <@{user}>, I couldn't understand the event command. Please check the format and try again.")
        

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

@flask_app.route("/slack/events", methods=["GET"])
def slack_challenge():
    challenge = request.args.get('challenge')
    return jsonify({"challenge": challenge})

if __name__ == "__main__":
    flask_app.run(port=3000)

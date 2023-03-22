import os
from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request


# Load environment variables
from dotenv import load_dotenv
load_dotenv()
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

# Define the message customization function
def create_custom_message(template, parameters):
    return template.format(**parameters)


# Send the customized message to a channel
def send_custom_message(channel_id, message_template, parameters):
    custom_message = create_custom_message(message_template, parameters)
    try:
        slack_client.chat_postMessage(channel=channel_id, text=custom_message)
    except SlackApiError as e:
        print(f"Error: {e}")

# Define the trigger word for your bot
trigger_word = "!deploy"
# Listen for app_mention events
@app.event("app_mention")
def handle_app_mentions(body, say):
    text = body["event"].get("text")
    if trigger_word in text:
        # Customize the message and parameters as needed
        message_template = "`[{customer}] [{environment}]` Deployment requested.\nDate/Time: {datetime}.\nExtra remarks: {remarks}"
        parameters = {
            "customer": "This is the parameter value",
            "environment": "production",
            "datetime": "2020-01-01 12:00:00",
            "remarks": "",
        }
        target_channel = "#deployments"
        send_custom_message(target_channel, message_template, parameters)

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

if __name__ == "__main__":
    flask_app.run(port=3000)

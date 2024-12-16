from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError
from env import SLACK_BOT_TOKEN, SLACK_APP_TOKEN
from db import create_question, get_question_by_tags

# Initializes your app with your bot token and socket mode handler
app = App(token=SLACK_BOT_TOKEN)
channel_id = None


def get_workspace_subdomain():
    try:
        # team.infoエンドポイントを呼び出し
        response = app.client.team_info()
        # ワークスペースのサブドメインを取得
        subdomain = response["team"]["domain"]
        print(f"Workspace Subdomain: {subdomain}")
        return subdomain
    except SlackApiError as e:
        print(f"Error fetching team info: {e.response['error']}")
        return None


subdomain = get_workspace_subdomain()


def get_message_url(channel_id, thread_ts):
    return f"https://{subdomain}.slack.com/archives/{channel_id}/p{thread_ts.replace('.', '')}"


@app.event("app_mention")
def set_activate_channel(event, say):
    text = event["text"]
    if "activate" in text:
        global channel_id
        channel_id = event["channel"]
        say(f"このチャンネルに対して質問を投稿します！")


@app.event("message")
def handle_message_on_dm(event, say, client):
    global channel_id
    global subdomain
    if channel_id is None:
        say("質問を投稿するチャンネルが設定されていません。")
        return
    text = event["text"]
    thread_ts = event.get("thread_ts")
    client.chat_postMessage(channel=channel_id, text=text)
    create_question({
        "channel_id": channel_id,
        "user_id": event["user"],
        "question": text,
        "thread_ts": thread_ts,
        "tags": ""
    })
    relative_questions = get_question_by_tags(text)
    message = ("質問を投稿しました！\n"
               f"{get_message_url(channel_id, thread_ts)}\n\n"
               "関連する質問\n"
               ''.join([get_message_url(q['channel_id'], q['thread_ts'])
                        for q in relative_questions])
               )
    say(message)


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()

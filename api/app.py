from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError
from env import SLACK_BOT_TOKEN, SLACK_APP_TOKEN, SLACK_BOT_USER_ID
from db import create_question, get_question_by_thread_ts, get_question_by_tags, get_question_by_question

CHANNEL_ID_FILE = "channel_id.txt"

# Initializes your app with your bot token and socket mode handler
app = App(token=SLACK_BOT_TOKEN)
channel_id = None
try:
    with open(CHANNEL_ID_FILE, "r") as f:
        channel_id = f.read()
except FileNotFoundError:
    pass


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


def get_message_url(channel_id, thread_ts, parent_ts=None):
    ts = thread_ts.replace('.', '')
    url = f"https://{subdomain}.slack.com/archives/{channel_id}/p{ts}"
    param = f"?thread_ts={parent_ts}&cid={channel_id}" \
        if parent_ts is not None else ""
    return url + param


def is_thread_message(event):
    return "thread_ts" in event \
        and event["thread_ts"] is not None \
        and event["thread_ts"] != event["ts"]


def activate_channel(cid):
    global channel_id
    channel_id = cid
    with open(CHANNEL_ID_FILE, "w") as f:
        f.write(channel_id)


@app.command("/activate")
def activate_channel_command(ack, say, command):
    activate_channel(command["channel_id"])
    say(f"このチャンネルに対して質問を投稿します！")


@app.event("app_mention")
def set_activate_channel(event, say):
    text = event["text"]


@app.event("message_posted")
def handle_message(event, say, client):
    global channel_id
    global subdomain
    # botが投稿した質問に対しての返信のみを処理
    if not is_thread_message(event) or event["parent_user_id"] != SLACK_BOT_USER_ID:
        return

    text = event["text"]
    thread_ts = event["thread_ts"]
    parent_message = get_question_by_thread_ts(thread_ts)
    if parent_message is None:
        say("質問の投稿が見つかりませんでした。")
        return

    message = ("質問に対する返信が来ました！\n"
               f"```{text}\n\n"
               "質問のURL: " +
               get_message_url(
                   parent_message["channel_id"], thread_ts) + "\n"
               "回答のURL: " + get_message_url(parent_message["channel_id"], event["ts"], thread_ts))
    client.chat_postMessage(channel=parent_message["dm_id"], text=message)


@ app.event("message")
def handle_message_on_dm(event, say, client):
    global channel_id
    global subdomain
    if channel_id is None:
        say("質問を投稿するチャンネルが設定されていません。")
        return
    text = event["text"]
    posted = client.chat_postMessage(channel=channel_id, text=text)
    dm_id = event["channel"]
    if not posted["ok"]:
        say(f"質問の投稿に失敗しました。\n{posted['error']}")
        return
    thread_ts = posted["ts"]

    tags = ",".join(["hoge", "test"])
    relative_questions = get_question_by_question(text)
    # relative_questions = get_question_by_tags(tags)
    relative_question_msg = ("関連する質問\n" +
                             '\n'.join([f"- {get_message_url(q['channel_id'], q['thread_ts'])}"
                                       for q in relative_questions])) if len(relative_questions) > 0 else "関連する質問はありません。"
    create_question({
        "channel_id": channel_id,
        "user_id": event["user"],
        "dm_id": dm_id,
        "question": text,
        "thread_ts": thread_ts,
        "tags": tags
    })
    message = ("質問を投稿しました！\n"
               f"{get_message_url(channel_id, thread_ts)}\n\n"
               f"{relative_question_msg}")

    # TODO: mrkdwnがうまくできない
    blocks = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": message
        }
    }]
    client.chat_postMessage(channel=dm_id, blocks=blocks, mrkdwn=True)


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()

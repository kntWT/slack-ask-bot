# Slack Ask Bot
情報検索特論2024 Gourp3

## 概要
先輩や先生などへの質問のハードルを下げるため，質問内容をBotを通して送信

## 説明
先輩や先生などへの質問のハードルを下げるため，質問内容をBotを通して送信できます．<br>
botに対してダイレクトメッセージを送ると指定したチャンネルにメッセージを転送します．<br>
スレッドに対して返信が来たらダイレクトメッセージで通知します．<br>
返信に対してさらに返信したい場合は，Botが教えてくれる質問番号（#xx）を先頭に書いてBotのダイレクトメッセージに送信すると，チャンネルの該当の質問のスレッドに転送されます．<br>
これで直接声をかけるのが怖い先輩や先生にも気軽に質問ができます．<br>
もしかしたら似たような質問を提示してくれるかもしれません．<br>

使い方
1. 質問を投稿したいチャンネルで`/activate`コマンドを打つ
2. Ask Botのダイレクトメッセージに対して質問を送る
3. チャンネルに転送された質問に対してスレッドで回答する
4. Ask Botのダイレクトメッセージで#質問番号を先頭につけて返信内容を送る
．．．

```text
例：
<Bot DM>
you: 好きな食べ物はなんですか？
bot: 質問を投稿しました！（#1）
        --- 質問のurl ---

<channel>
bot: 好きな食べ物はなんですか？
        someone（スレッド）: カレーです！

<Bot DM>
bot: 質問に対する返信が来ました！（#1）
        ```カレーです！
        ---質問のurl---
        ---回答のurl---
you: #1
        僕はラーメンが好きです
bot: 返信を転送しました！（#1）
        ----返信のurl----

<channel>
bot: 好きな食べ物はなんですか？
        someone（スレッド）: カレーです！
        bot（スレッド）: 僕はラーメンが好きです

# 休講Bot

## 依存関係のインストール
```
pip install pymongo bs4 requests
```
## 起動
```
mkdir ~/repos/wd-kyukou-bot/db
mongod --dbpath ~/repos/wd-kyukou-bot/db --port 8070
python3 run.py
```

## リポジトリ構成
* uec-world-dominators/kyukou-bot
* <自分のid>/kyukou-bot (forked)\
各自こっちで編集、できたら上のリポジトリにプルリクエスト
<!-- 1. https://github.com/uec-world-dominators/kyukou-bot にアクセスして自分のアカウントにForkする
2. 自分のアカウント内の「kyukou-bot」リポジトリをCloneする
3. `git remote add upstream https://github.com/uec-world-dominators/kyukou-bot`をターミナルで実行する
4. 編集する
5. vscodeなりターミナルなりでコミットする
6. pushする
7. ある程度できたらgithub.comからuec-world-dominators/kyukou-bot devブランチ宛にプルリクエストをさくせいする
8. みんながチェックして良かったらマージする -->

```
# 上位のリポジトリを設定
git remote add upstream https://github.com/uec-world-dominators/kyukou-bot
# そこから他の人が変更したものを取ってくる
git fetch upstream dev
# 自分の変更と競合しないように合体する
git merge upstream/dev
```

## LINE

```json
// メッセージが送られてきたとき
{
   "events":[
      {
         "type":"message",
         "replyToken":"32 len str",
         "source":{
            "userId":"'U' + 32 len str",
            "type":"user"
         },
         "timestamp":1568774687578,
         "message":{
            "type":"text",
            "id":"14 len str",
            "text":"aa"
         }
      }
   ],
   "destination":"'U' + 32 len str"
}
```

```json
// 友だち追加したとき
{
   "events":[
      {
         "type":"follow",
         "replyToken":"32 len str",
         "source":{
            "userId":"'U' + 32 len str",
            "type":"user"
         },
         "timestamp":1568774945957
      }
   ],
   "destination":"'U' + 32 len str"
}
```

```json
// ブロックしたとき
{
   "events":[
      {
         "type":"unfollow",
         "source":{
            "userId":"'U' + 32 len str",
            "type":"user"
         },
         "timestamp":1568774870089
      }
   ],
   "destination":"'U' + 32 len str"
}
```
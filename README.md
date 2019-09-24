# 休講Bot


## 依存関係のインストール
```sh
pip install pymongo bs4 requests pyyaml
```

## 起動
* Access TokenとChannel Secretは環境変数に設定する
```sh
./run
```

## IO

```

line bot csv コピペ--\
                      \
csv upload link    -----------> LINE Bot
                      /
画面コピペ to web   --/

```


## リポジトリ構成
* uec-world-dominators/kyukou-bot
* <自分のid>/kyukou-bot (forked)\
各自こっちで編集、できたら上のリポジトリにプルリクエスト
1. https://github.com/uec-world-dominators/kyukou-bot にアクセスして自分のアカウントにForkする
2. 自分のアカウント内の「kyukou-bot」リポジトリをCloneする
3. `git remote add upstream https://github.com/uec-world-dominators/kyukou-bot`をターミナルで実行する
4. 編集する
5. vscodeなりターミナルなりでコミットする
6. pushする
7. ある程度できたらgithub.comからuec-world-dominators/kyukou-bot devブランチ宛にプルリクエストをさくせいする
8. みんながチェックして良かったらマージする

```sh
# 上位のリポジトリを設定
git remote add upstream https://github.com/uec-world-dominators/kyukou-bot
# そこから他の人が変更したものを取ってくる
git fetch upstream dev
# 自分の変更と競合しないように合体する
git merge upstream/dev
```

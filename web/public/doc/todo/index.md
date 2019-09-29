---
title: TODO
---

# tomy-0000

通知キュー

* 絶対時間に直した通知を入れていく
* 過ぎたら削除
* sniper-flyの設定で変更があったら全て消して作り直す
* tommy-0000の関数を呼びまくるのは負荷が高いので、通知を発行するだけの関数を作る
* hashとtimeを見て同じものがなかったら追加する
```py
'users_db.queue': [{
        'hash': スクレイピング結果のhash,
        'time': 15000000,
        'message': ''
}]
```

# yyuusseeii
* メインWEBページ
* ドキュメント整備(markdown+pandoc)
* 年度指定を自動化する（今2019って手打ちしてる）
* スクレイピング結果のhashには年度を入れたほうがいいかも

```py
"hash":hashlib.sha256((str(2019)+tr.text).encode()).hexdigest()
#こんなかんじ
```

# sniper-fly
TwitterとLINEの設定関連

* 配信時間・配信時間一覧・削除追加
* メールアドレスとの連携解除等

> Procedureを単体デバッグできるようにしたよ

# shosatojp

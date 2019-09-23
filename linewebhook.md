
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
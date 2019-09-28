from . import twitter_api


def direct_message(user_id, msg_text):
    print(user_id, msg_text)
    twitter_api.send(user_id, msg_text)


def follow(user_id):
    print(f'Followed by {user_id}')
    twitter_api.send(user_id, 'フォローありがとうございます！！！')
from . import line_api


def follow(user_id):
    print(f'followed by {user_id}')
    line_api.reply(user_id, 'こんにちは')


def unfollow(user_id):
    print(f'unfollowed by {user_id}')


def message(user_id, msg_text):
    print(f'message from {user_id}: {msg_text}')
    line_api.reply(user_id, msg_text)

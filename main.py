import os
import json
from datetime import datetime, timezone, timedelta

from zoomus import ZoomClient
import telegram
from dotenv import load_dotenv


load_dotenv()


def main():

    # Get zoom client
    zoom_client = ZoomClient(api_key=os.environ['ZOOM_API_KEY'], api_secret=os.environ['ZOOM_API_SECRET'])

    # Get current open zoom meetings
    response = zoom_client.meeting.list(user_id=os.environ['ZOOM_USER_ID'])
    open_meetings = json.loads(response.content)

    # Delete old zoom meetings
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    for meeting in open_meetings['meetings']:
        dt = datetime.strptime(meeting['start_time'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        if dt < now - timedelta(hours=1):
            zoom_client.meeting.delete(id=meeting['id'])

    # Create new zoom meeting
    response = zoom_client.meeting.create(
        user_id=os.environ['ZOOM_USER_ID'],
        settings=dict(join_before_host=True, waiting_room=False),
    )
    new_meeting = json.loads(response.content)

    # Create a telegram bot
    bot = telegram.Bot(token=os.environ['TELEGRAM_BOT_TOKEN'])

    # Send zoom join url through telegram bot
    bot.send_message(chat_id=os.environ['TELEGRAM_CHAT_ID'], text=new_meeting['join_url'])


if __name__ == '__main__':
    main()

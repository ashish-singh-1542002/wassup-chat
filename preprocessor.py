import re
import pandas as pd
def preprocess(data):
    pattern = '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s(?:am|pm)\s-\s'
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)
    
    df = pd.DataFrame({'user_message': messages, 'date': dates})

    # rename
    df.rename(columns={'date': 'message_date'}, inplace=True)

    # correct datetime conversion
    df['message_date'] = pd.to_datetime(
        df['message_date'],
        format='%d/%m/%y, %I:%M %p - '
    )

    # optional: rename back
    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []

    for msg in df['user_message']:
        entry = re.split(r'([\w\s]+):\s', msg, maxsplit=1)

        if len(entry) > 2:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    # loop ke baad dataframe update
    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)
    df['month'] = df['date'].dt.month_name()
    df['minute'] = df['date'].dt.minute
    df['hour'] = df['date'].dt.hour
    df['day'] = df['date'].dt.day
    
    return df
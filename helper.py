from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
extract = URLExtract()



def fetch_stats(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # fetch the number of messages
    num_messages = df.shape[0]

    # fetch the total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # fetch number of media messages
    num_media_messages = df['message'].str.contains(
        '\.(jpg|jpeg|png|gif|mp4|avi|mov|pdf|docx|xlsx|pptx)\s*\(file attached\)',
        case=False,
        regex=True
    ).sum()

    # fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages,len(words),num_media_messages,len(links)

def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x,df
def create_wordcloud(selected_user,df):

    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500,height=500,min_font_size=10,background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc
def most_common_words(selected_user,df):

    f = open('stop_hinglish.txt','r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []

    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df
def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])

    emoji_df = pd.DataFrame(
        Counter(emojis).most_common(len(Counter(emojis))),
        columns=['emoji', 'count']
    )

    return emoji_df
def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # 🔑 Ensure date features exist
    df['date'] = pd.to_datetime(df['date'])

    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()

    timeline = (
        df.groupby(['year', 'month_num', 'month'])
          .count()['message']
          .reset_index()
          .sort_values(['year', 'month_num'])
    )

    timeline['time'] = timeline['month'] + '-' + timeline['year'].astype(str)

    return timeline

def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # 🔑 Ensure date column exists and is datetime
    df['date'] = pd.to_datetime(df['date'])

    # 🔑 Create only_date safely
    df['only_date'] = df['date'].dt.date

    daily_timeline = (
        df.groupby('only_date')
          .count()['message']
          .reset_index()
    )

    return daily_timeline


def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    #  Ensure date features exist
    df['date'] = pd.to_datetime(df['date'])
    df['day_name'] = df['date'].dt.day_name()

    return df['day_name'].value_counts()


def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # 🔑 Ensure datetime
    df['date'] = pd.to_datetime(df['date'])

    # 🔑 Day name
    df['day_name'] = df['date'].dt.day_name()

    # 🔑 Hour
    df['hour'] = df['date'].dt.hour

    # 🔑 Period (hour slots)
    period = []
    for h in df['hour']:
        if h == 23:
            period.append('23-00')
        else:
            period.append(f'{h:02d}-{h+1:02d}')
    df['period'] = period

    user_heatmap = df.pivot_table(
        index='day_name',
        columns='period',
        values='message',
        aggfunc='count'
    ).fillna(0)

    return user_heatmap

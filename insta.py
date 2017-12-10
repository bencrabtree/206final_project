#information information
#information and stuff
#access token goes here
import unittest, sqlite3, json, requests, datetime, calendar, csv
from pprint import pprint

access_token = "219495618.a8f2717.e15485b93a5442abbae5ad9cc7b00e3c"
# instagram_client_secret = "82e8bee6d9d14d1ca9a8f0fc48908bd9"

# Set up Instgram cache file
CACHE_FNAME = "insta_cache.json"
try:
    cache_file = open(CACHE_FNAME,'r')
    cache_contents = cache_file.read()
    cache_file.close()
    CACHE_DICTION = json.loads(cache_contents)
except:
    CACHE_DICTION = {}

# Get instagram post data depending on user
def get_data(access_token_in):
    data = 'https://api.instagram.com/v1/users/self/media/recent/?access_token={}'.format(access_token_in)
    posts_str = requests.get(data).text
    posts = json.loads(posts_str)['data']
    user_id = posts[0]['user']['id']

    if user_id in CACHE_DICTION:
        print ("insta using cache")
        insta_data = CACHE_DICTION[user_id]
    else:
        print ("insta fetching")
        data_tups = []
        for post in posts:
            timestamp = datetime.datetime.fromtimestamp(int(post['created_time']))
            weekday = calendar.day_name[timestamp.weekday()]
            data_tups.append((post['user']['id'], post['likes']['count'], weekday))

        CACHE_DICTION[user_id] = list(data_tups)
        insta_data = data_tups
        filename = open(CACHE_FNAME, 'w')
        filename.write(json.dumps(CACHE_DICTION))
        filename.close()
    return insta_data

# Sort data into a dictionary sorted by weekday
def weekly_results(list_of_data):
    user_id = list_of_data[0][0]
    weekday_dict = {"Monday": {"posts": 0, "likes": 0}, "Tuesday": {"posts": 0, "likes": 0},
    "Wednesday": {"posts": 0, "likes": 0}, "Thursday": {"posts": 0, "likes": 0},
    "Friday": {"posts": 0, "likes": 0}, "Saturday": {"posts": 0, "likes": 0},
    "Sunday": {"posts": 0, "likes": 0}}
    for post in list_of_data:
        if post[2] == "Monday":
            weekday_dict["Monday"]['posts'] += 1
            weekday_dict["Monday"]['likes'] += post[1]
        elif post[2] == "Tuesday":
            weekday_dict["Tuesday"]['posts'] += 1
            weekday_dict["Tuesday"]['likes'] += post[1]
        elif post[2] == "Wednesday":
            weekday_dict["Wednesday"]['posts'] += 1
            weekday_dict["Wednesday"]['likes'] += post[1]
        elif post[2] == "Thursday":
            weekday_dict["Thursday"]['posts'] += 1
            weekday_dict["Thursday"]['likes'] += post[1]
        elif post[2] == "Friday":
            weekday_dict["Friday"]['posts'] += 1
            weekday_dict["Friday"]['likes'] += post[1]
        elif post[2] == "Saturday":
            weekday_dict["Saturday"]['posts'] += 1
            weekday_dict["Saturday"]['likes'] += post[1]
        else:
            weekday_dict["Sunday"]['posts'] += 1
            weekday_dict["Sunday"]['likes'] += post[1]
    average_likes = {}
    for weekday in weekday_dict:
        if weekday_dict[weekday]['posts'] != 0:
            average_likes[weekday] = (weekday_dict[weekday]['likes'] / weekday_dict[weekday]['posts'])
        else:
            average_likes[weekday] = weekday_dict[weekday]['likes']
    average_likes["User ID"] = int(user_id)
    return average_likes

def get_user_id(list_of_data):
    return list_of_data[0][0]

user_id = get_user_id(get_data(access_token))
 # Need to set up SQL database and insert instagram table into it
def write_to_sql(weekly_data, sql_filename):
    conn = sqlite3.connect(sql_filename)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS Insta_AvgLikes")
    cur.execute("""CREATE TABLE Insta_AvgLikes (user_id NUMBER, Monday NUMBER, Tuesday NUMBER,
                    Wednesday NUMBER, Thursday NUMBER, Friday NUMBER, Saturday NUMBER, Sunday NUMBER)""")
    tup = (weekly_data["User ID"], weekly_data['Monday'], weekly_data['Tuesday'], weekly_data['Wednesday'], weekly_data['Thursday'], weekly_data['Friday'], weekly_data['Saturday'], weekly_data['Sunday'])
    cur.execute('INSERT INTO Insta_AvgLikes (user_id, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday) VALUES (?,?,?,?,?,?,?,?)', tup)
    conn.commit()

    cur.close()

def sql_to_csv(sql_filename, csv_filename):
    conn = sqlite3.connect(sql_filename)
    cur = conn.cursor()
    cur.execute('SELECT * FROM Insta_AvgLikes')

    row = cur.fetchall()
    with open(csv_filename, 'w', newline='') as fp:
        data = csv.writer(fp, delimiter=',')
        data.writerows(row)

    cur.close()

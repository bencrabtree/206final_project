### Ben Crabtree, SI 206 Final Project ###
# USING: Facebook, Instagram
import info
import unittest, sqlite3, json, requests, datetime, calendar, csv, facebook, instagram
from pprint import pprint

CACHE_FNAME = "fb_cache.json"
try:
    cache_file = open(CACHE_FNAME,'r')
    cache_contents = cache_file.read()
    cache_file.close()
    CACHE_DICTION = json.loads(cache_contents)
except:
    CACHE_DICTION = {}

# EFFECTS: returns a list of tuples, each tuple corresponds to a unique post
# in each tuple there is a weekday and the amount of people tagged
def get_fb_data(access_token_in):
    graph = facebook.GraphAPI(access_token=access_token_in, version="2.1")
    tagged_pics = graph.request('me?fields=photos.limit(100){tags{name},created_time,likes}')
    user_id = tagged_pics['id']
    list_of_pics = tagged_pics['photos']['data']
    data = []
    # use cache if this was already searcheds
    if user_id in CACHE_DICTION:
        print("using cache")
        data = CACHE_DICTION[user_id]
    # fetch if not
    else:
        print("fetching")
        for pic in list_of_pics:
            time = pic['created_time']
            y, m, d = (int(time.split('-')[0]), int(time.split('-')[1]), int(time.split('-')[2][:2]))
            weekday = calendar.day_name[datetime.datetime(y, m, d).weekday()]

            tags = pic['tags']['data']
            names = []
            for tag in tags:
                names.append(tag['name'])

            like_count = 0
            if 'likes' in pic.keys():
                for like in pic['likes']:
                    like_count += 1

            data.append((weekday, len(names), like_count))

        CACHE_DICTION[user_id] = data
        filename = open(CACHE_FNAME, 'w')
        filename.write(json.dumps(CACHE_DICTION))
        filename.close()
    return data

# EFFECTS: takes in a list of data (from get_fb_data), returns a dictionary
# with the key being the weekday and the value being the average amount of tags per post
def get_weekly_results(list_of_data):
    # initialize dictionary to store my data in
    weekday_dict = {"Monday": {"posts": 0, "people_tagged": 0, "likes": 0}, "Tuesday": {"posts": 0, "people_tagged": 0, "likes": 0},
    "Wednesday": {"posts": 0, "people_tagged": 0, "likes": 0}, "Thursday": {"posts": 0, "people_tagged": 0, "likes": 0},
    "Friday": {"posts": 0, "people_tagged": 0, "likes": 0}, "Saturday": {"posts": 0, "people_tagged": 0, "likes": 0},
    "Sunday": {"posts": 0, "people_tagged": 0, "likes": 0}}
    for post in list_of_data:
        if post[0] == "Monday":
            weekday_dict["Monday"]['posts'] += 1
            weekday_dict["Monday"]['people_tagged'] += post[1]
            weekday_dict["Monday"]['likes'] += post[2]
        elif post[0] == "Tuesday":
            weekday_dict["Tuesday"]['posts'] += 1
            weekday_dict["Tuesday"]['people_tagged'] += post[1]
            weekday_dict["Tuesday"]['likes'] += post[2]
        elif post[0] == "Wednesday":
            weekday_dict["Wednesday"]['posts'] += 1
            weekday_dict["Wednesday"]['people_tagged'] += post[1]
            weekday_dict["Wednesday"]['likes'] += post[2]
        elif post[0] == "Thursday":
            weekday_dict["Thursday"]['posts'] += 1
            weekday_dict["Thursday"]['people_tagged'] += post[1]
            weekday_dict["Thursday"]['likes'] += post[2]
        elif post[0] == "Friday":
            weekday_dict["Friday"]['posts'] += 1
            weekday_dict["Friday"]['people_tagged'] += post[1]
            weekday_dict["Friday"]['likes'] += post[2]
        elif post[0] == "Saturday":
            weekday_dict["Saturday"]['posts'] += 1
            weekday_dict["Saturday"]['people_tagged'] += post[1]
            weekday_dict["Saturday"]['likes'] += post[2]
        else:
            weekday_dict["Sunday"]['posts'] += 1
            weekday_dict["Sunday"]['people_tagged'] += post[1]
            weekday_dict["Sunday"]['likes'] += post[2]

        # get the average tags per weekday
    avg_tags = {}
    for day in weekday_dict.keys():
        numppl = weekday_dict[day]['people_tagged']
        numpics = weekday_dict[day]['posts']
        numlikes = weekday_dict[day]['likes']
        avg_tag = numppl / numpics
        avg_likes = numlikes / numpics
        avg_tags[day] = (avg_tag, avg_likes)

    return avg_tags

def write_averages(averages_dict):
    conn = sqlite3.connect("facebook_data.sqlite")
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS Facebook_Averages")
    cur.execute("CREATE TABLE Facebook_Averages (Weekday TEXT, AvgLikes NUMBER, AvgTags NUMBER)")

    for day in averages_dict.keys():
        tup = (day, averages_dict[day][1], averages_dict[day][0])
        cur.execute('INSERT INTO Facebook_Averages (Weekday, AvgLikes, AvgTags) VALUES (?,?,?)', tup)
        conn.commit()

    cur.execute('SELECT * FROM Facebook_Averages')
    row = cur.fetchall()
    with open("facebook_averages.csv", 'w', newline='') as fp:
        data = csv.writer(fp, delimiter=',')
        data.writerows(row)

    cur.close()

# EFFECTS: takes in a dictionary of data and writes it to sql file and csv
def write_sql_csv(facebook_data):
    conn = sqlite3.connect("facebook_data.sqlite")
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS Facebook_Data")
    cur.execute("""CREATE TABLE Facebook_Data (Weekday TEXT,
                    Num_Tags NUMBER, Num_Likes NUMBER)""")
    for data in facebook_data:
        tup = (data[0], data[1], data[2])
        cur.execute('INSERT INTO Facebook_Data (Weekday, Num_Tags, Num_Likes) VALUES (?,?,?)', tup)
        conn.commit()

    cur.execute('SELECT * FROM Facebook_Data')
    # i used csv.writer to easily write my data from sql to csv file
    row = cur.fetchall()
    with open("facebook_data.csv", 'w', newline='') as fp:
        data = csv.writer(fp, delimiter=',')
        data.writerows(row)

    cur.close()

data = get_fb_data(info.fb_access_token)
write_sql_csv(data)
avgs = get_weekly_results(data)
write_averages(avgs)

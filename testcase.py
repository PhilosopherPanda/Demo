import feedparser
import pyrebase
from discord_webhook import DiscordWebhook, DiscordEmbed
from dateutil import parser, tz
import time
import os



def run_bot():
    NewsFeed = feedparser.parse('https://nyaa.si/?page=rss&u=superelmo')
    
    entry_ids = [entry.id for entry in reversed(NewsFeed.entries[:limit+threshold])]

    blacklist = [item for item in blacklist if item in entry_ids]

    for entry in reversed(NewsFeed.entries[:limit]):
        if entry.id not in blacklist:
            dt = parser.parse(entry.published)
            local_time = dt.astimezone(tz.gettz("Asia/Jakarta"))
            local_time = local_time.strftime("%a, %d %b %Y, %H:%M:%S")

            embed = DiscordEmbed(title=entry.title, description='{}\n{}'.format(entry.id, local_time), color=29183)
            embed.add_embed_field(name='Hash', value=entry.nyaa_infohash, inline=True)
            embed.add_embed_field(name='Size', value=entry.nyaa_size, inline=True)
            
            embed.set_timestamp()
            webhook.add_embed(embed)

            webhook.execute()
            # print("New post found, sending to Discord")
            webhook.remove_embed(0)

            blacklist.append(str(entry.id))
            if len(blacklist) > limit + threshold:
                blacklist.pop(0)
            with open("seen_vn.txt", "w") as f:
                for item in blacklist:
                    f.write(str(item) + "\n")
            
            storage.child("seen_vn.txt").put("seen_vn.txt")

        time.sleep(15)


def blacklisted_posts():
    blacklist = list()
    if os.path.isfile("seen_vn.txt"):
        with open("seen_vn.txt", "r") as f:
            lines = f.read()
            lines = lines.strip().split("\n")
            for line in lines:
                blacklist = blacklist.append(line.strip())

    return blacklist


if __name__ == "__main__":
    webhook_urls = ['https://discord.com/api/webhooks/793451858422188276/KW8jvY6U2bCgQjwFirdUNEm_N-Y4m8C5Riq-_wpMl_yEJ2POa2W15WYg6lBzyRC_jVsl']
    webhook = DiscordWebhook(url=webhook_urls)
    limit = 10
    threshold = 5

    firebaseConfig = {
        'apiKey': "gAAAAABi6UnZsZPodYr3T9SGOZl5g49mNkMVPJYBaLBbGgd09Bqdzccpu9dD2ZLg6uyeJnvQ3yik6krPOboJ9tYp_o7s3SIuWojTwU3zoaBGMM6KixJCWEc5oxMoJcaFF1VCy7RuNUyy",
        'authDomain': "vnscraping.firebaseapp.com",
        'databaseURL': "https://vnscraping.firebaseio.com",
        'projectId': "vnscraping",
        'storageBucket': "vnscraping.appspot.com",
        'messagingSenderId': "244835616221",
        'appId': "1:244835616221:web:e182bfdf7e7b7beb102234"
    }

    firebase = pyrebase.initialize_app(firebaseConfig)

    storage = firebase.storage()
    storage.child("seen_vn.txt").download("seen_vn.txt")

    blacklist = blacklisted_posts()

    while True:
        run_bot()

from datetime import datetime, timedelta, timezone
import uuid

from django.contrib.auth.models import User
from django.db import models

import bs4
import requests

from core import cache

class Item(models.Model):
    identifier = models.UUIDField(default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(
        'Subscription',
        on_delete=models.CASCADE,
        related_name='items',
    )
    is_read = models.BooleanField(default=False)
    link = models.URLField(blank=True, null=True)
    title = models.CharField(blank=True, max_length=256, null=True)
    author = models.CharField(blank=True, max_length=64, null=True)
    description = models.CharField(blank=True, max_length=256, null=True)
    content = models.CharField(blank=True, max_length=2048, null=True)

@cache.memoize(timeout=3600)
def get_feed_uri(uri):
    response = requests.get(uri)
    assert response.status_code == 200
    return response.content

class Subscription(models.Model):
    identifier = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feed_uri = models.URLField()
    most_recent_refresh_utc = models.DateTimeField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    title = models.CharField(blank=True, max_length=256, null=True)
    description = models.CharField(blank=True, max_length=256, null=True)

    def refresh(self):
        now = datetime.now(timezone.utc)

        if self.most_recent_refresh_utc and self.most_recent_refresh_utc > (now - timedelta(hours=1)):
            return

        feed_content = get_feed_uri(self.feed_uri)
        soup = bs4.BeautifulSoup(feed_content, 'html.parser')

        if soup.rss and soup.rss.channel:
            channel = soup.rss.channel

            if channel.title and channel.title.text:
                self.title = channel.title.text

            if channel.description and channel.description.text:
                self.description = channel.description.text

            if channel.link and channel.link.text:
                self.link = channel.link.text

            item_nodes = channel.find_all('item', recursive=False)

            items_raw = []

            for item_node in  item_nodes:
                item_raw = {}

                if item_node.title and item_node.title.text:
                    item_raw['title'] = item_node.title.text
                if item_node.description and item_node.description.text:
                    item_raw['description'] = item_node.description.text

                if item_node.link and item_node.link.text:
                    item_raw['link'] = item_node.link.text
                else:
                    permalink_node = item_node.find('guid', {'ispermalink': True}, recurse=False)
                    if permalink_node and permalink_node.text:
                        item_raw['link'] = permalink_node.text

                if item_node.pubdate and item_node.pubdate.text:
                    item_raw['published_date'] = item_node.pubdate.text

                if item_node.find('dc:creator', recursive=False) and item_node.find('dc:creator').text:
                    item_raw['author'] = item_node.find('dc:creator', recursive=False).text

                if item_node.content and item_node.content.text:
                    item_raw['content'] = item_node.content.text
                else:
                    content_node = item_node.find('content:encoded', recursive=False)
                    if content_node.text:
                        item_raw['content'] = content_node.text

                items_raw.append(item_raw)

        elif soup.feed:
            feed = soup.feed

            if feed.title and feed.title.text:
                self.title = feed.title.text

            if feed.description and feed.description.text:
                self.description = feed.description.text

            link = feed.find('link', rel='alternate', recursive=False)

            if link and link.get('href'):
                self.link = link['href']

            items_raw = []

            for entry in feed.find_all('entry', recursive=False):
                i = {}

                if entry.title and entry.title.text:
                    i['title'] = entry.title.text

                link = entry.find('link', rel='alternate', recursive=False)

                if link and link.get('href'):
                    i['link'] = link['href']

                if entry.published and entry.published.text:
                    i['published_date'] = entry.published.text

                if entry.author and entry.author.find('name', recursive=False) and entry.author.find('name', recursive=False).text:
                    i['author'] = entry.author.find('name', recursive=False).text

                items_raw.append(i)

        else:
            # soup.rss or soup.rss.channel was falsey
            # soup.feed was also falsey
            import ipdb; ipdb.set_trace()

        # Items without links are pretty useless, discard them
        items_raw = [i for i in items_raw if i.get('link')]

        self.items.exclude(
            link__in= set(i['link'] for i in items_raw if i.get('link'))
        ).delete()

        for i in items_raw:
            # TODO Published dates are coming in in format
            # Thu, 18 Feb 2021 20:51:42 GMT
            # Save them!
            item, created = Item.objects.update_or_create(
                link=i['link'],
                defaults={
                    'subscription': self,
                    'title': i.get('title'),
                    'author': i.get('author'),
                    'description': i.get('description'),
                    'content': i.get('content'),
                }
            )

        self.most_recent_refresh_utc = now
        self.save()

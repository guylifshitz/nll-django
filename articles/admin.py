from django.contrib import admin

from articles.models import Rss_feeds, open_subtitles
admin.site.register(Rss_feeds)
admin.site.register(open_subtitles)

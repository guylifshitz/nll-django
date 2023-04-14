from django.contrib import admin

from words.models import Words, Flexions, WordRatings

admin.site.register(Words)
admin.site.register(Flexions)
admin.site.register(WordRatings)



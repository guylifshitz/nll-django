from django.contrib import admin

from words.models import Word, Flexion, WordRating

admin.site.register(Word)
admin.site.register(Flexion)
admin.site.register(WordRating)

from django.contrib import admin
from .models import Schools, Teams

@admin.register(Schools)
class SchoolsAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'email')
    search_fields = ('name', 'city')

@admin.register(Teams)
class TeamsAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'captain', 'patron')
    filter_horizontal = ('members',)

from django.contrib import admin

from MovieColorSchemer.models import *

# Register your models here.
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
	list_display = ['title', 'datasetType', 'dirName']

@admin.register(Cost)
class CostAdmin(admin.ModelAdmin):
	list_display = ['movietitle', 'datasetType', 'shotNo', 'frameNo', 'keyframe', 'clearness', 'representativeness', 'saliency']



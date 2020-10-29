from django.shortcuts import render
from django.conf import settings
from django.forms.models import model_to_dict
from django.db.models import F, Sum, Avg, Value

from chartit import DataPool, Chart

import os
import natsort
import numpy as np

from MovieColorSchemer.models import *

import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from DSIIL.ConvexHull_Simplification.color_merger import merge_colors

# Create your views here.
def moviePicker(request):
	movieList = Movie.objects.all()
	return render(request, 'moviePicker.html', {'movieList': movieList})

def shotList(request, movieName=""):
	movie = Movie.objects.get(dirName=movieName)
	shotPath = os.path.join('saliencies', movie.datasetType, movie.dirName)

	shots = []
	shotDirs = os.listdir(os.path.join(settings.MEDIA_ROOT, shotPath));
	shotDirs = natsort.natsorted(shotDirs, reverse=False)
	for d in shotDirs:
		if d.startswith("shot-"):    
			shots.append(d.replace("shot-", ""))

	rgb_colors = merge_colors(movie.dirName, movie.datasetType, 0)
	rgb_colors = tuple(map(tuple, np.reshape(rgb_colors, [len(rgb_colors), 3])))
	hex_colors = ['#%s' % ''.join(['%02x' % c for c in rgb_color]) for rgb_color in rgb_colors]

	# hex_colors = ['#%s' % ''.join(['%02x' % c for c in tuple(map(tuple, rgb_color))]) for rgb_color in rgb_colors]

	return render(request, 'movieShots.html', {'movie': movie, 'shotIDs': shots, 'colors': hex_colors})

def movieContents(request, movieName="", shotID=1):
	movie = Movie.objects.get(dirName=movieName)
	imagePath = os.path.join('saliencies', movie.datasetType, movie.dirName, ('shot-%d' % shotID))

	frame_data = []
	imageFiles = os.listdir(os.path.join(settings.MEDIA_ROOT, imagePath));
	imageFiles = natsort.natsorted(imageFiles, reverse=False)
	for f in imageFiles:
		if f.endswith("-frame.jpg"):
			frameNo = f.replace('-frame.jpg', '')

			costs = Cost.objects.filter(movietitle=movie.dirName, shotNo=shotID, frameNo=frameNo).values().first()
			frame_data.append({
				'frameNo': frameNo,
				'keyframe': costs['keyframe'],
				'representativeness': costs['representativeness'], 
				'saliency': costs['saliency'],
				'clearness': costs['clearness'], 
				'img': os.path.join(settings.MEDIA_URL, imagePath, f),
				})

	costData = DataPool(
		series=
		[{'options': {
			'source': Cost.objects.filter(movietitle=movie.dirName, shotNo=shotID)
					.annotate(cost_sum=Value(0.5)*F('clearness')
							+ Value(1.0)*F('representativeness')
							+ Value(0.1)*F('saliency'))},
		'terms' : [
			'frameNo',
			'cost_sum',
			'clearness',
			'representativeness',
			'saliency']}
		])

	costChart = Chart(
    	datasource = costData,
    	series_options =
		[{'options':{
			'type': 'line',
			'stacking': False},
		'terms':{
			'frameNo': [
				'clearness',
				'representativeness',
				'saliency',
				'cost_sum']
		}}],
		chart_options =
		{'title': {
			'text': 'Frame Costs'},
		'xAxis': {
			'title': {
			'text': 'Frame No.'}}})


	return render(request, 'movie.html', {'movie': movie, 'shotID': shotID,
		'frame_data': frame_data, 'costChart': costChart})


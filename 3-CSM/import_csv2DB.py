import csv
import os
import natsort
import math

from MovieColorSchemer.models import Cost
from MovieColorSchemer.models import Movie

result_path = os.path.join('..', 'results')
result_clustering_path = os.path.join(result_path, 'clustering')
dataset_types = ['OVSD', 'CMD']
movie_titles = []

def camelCase(st):
    output = ''.join(x for x in st.title() if x.isalnum())
    return output[0].lower() + output[1:]

for dataset_type in dataset_types:
	dataset_dir_path = os.path.join(result_clustering_path, dataset_type)
	if os.path.isdir(dataset_dir_path):
		for movie_title in os.listdir(dataset_dir_path):
			if not os.path.isdir(os.path.join(dataset_dir_path, movie_title)):
				continue
			movie_titles.append((dataset_type, movie_title))

instances = []
for dataset_type, movie_title in movie_titles:
	instances.append(Movie(
		title=camelCase(movie_title.replace('-', ' ')),
		datasetType=dataset_type,
		dirName=movie_title))

Movie.objects.bulk_create(instances)

for dataset_type, movie_title in movie_titles:
	print('Processing ', dataset_type, movie_title)

	cost_csv_lists = [f for f in os.listdir(os.path.join(result_clustering_path, dataset_type, movie_title)) if f.endswith('-costs.csv')]
	cost_csv_lists = natsort.natsorted(cost_csv_lists, reverse=False)

	for csvFile in cost_csv_lists:
		shot_no = csvFile.replace(movie_title, '').replace('-costs.csv', '').replace('-', '')

		with open(os.path.join(result_clustering_path, dataset_type, movie_title, csvFile)) as f:
			reader = csv.reader(f, delimiter=',', skipinitialspace=True)
			_ = next(reader)

			instances = []
			for row in reader:
				representativeness = float(row[4])
				if math.isnan(representativeness):
					representativeness = 0

				instances.append(Cost(
					movietitle=movie_title,
					datasetType=dataset_type,
					shotNo=int(shot_no),
					frameNo=int(row[0]),
					keyframe=int(row[1]),
					clearness=float(row[2]),
					saliency=float(row[3]),
					representativeness=representativeness))

			Cost.objects.bulk_create(instances)

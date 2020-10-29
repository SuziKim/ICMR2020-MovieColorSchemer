from django.db import models

# Create your models here.
class Movie(models.Model):
	title = models.CharField(max_length=100, default='')
	datasetType = models.CharField(max_length=100, default='')
	dirName = models.CharField(max_length=100, default='')

class Cost(models.Model):
	movietitle = models.CharField(max_length=100, default='')
	datasetType = models.CharField(max_length=100, default='')
	shotNo = models.IntegerField(default=0)
	frameNo = models.IntegerField(default=0)
	keyframe = models.IntegerField(default=0)
	clearness = models.FloatField(default=0)
	representativeness = models.FloatField(default=0)
	saliency = models.FloatField(default=0)

	def __str__(self):
		return '%s-%s-%d-%d' % (self.datasetType, self.movietitle, self.shotNo, self.frameNo)

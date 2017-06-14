from __future__ import unicode_literals

from django.db import models

class Post(models.Model):
	author = models.CharField(max_length=128, blank=False)
	timestamp = models.DateTimeField(auto_now_add=True)
	heading = models.TextField()
	content = models.TextField()
	image = models.ImageField(blank=True)

	def __unicode__(self):
		return self.id

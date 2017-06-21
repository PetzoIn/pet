from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User

class UserProfile(models.Model):
	user = models.ForeignKey(User)
	name = models.CharField(blank=True, max_length=128)
	phone = models.CharField(blank=True, max_length=10)
	address = models.TextField(blank=True)

	def __unicode__(self):
		return self.name

class Dog(models.Model):
	owner = models.ForeignKey(User)
	name = models.CharField(blank=False, max_length=128)
	breed = models.TextField(blank=False)
	age = models.CharField(blank=False, max_length=10)
	gender = models.CharField(blank=False, max_length=6)
	weight = models.IntegerField(blank=False)
	bodyCondition = models.CharField(blank=False, max_length=128)
	activity = models.CharField(blank=False, max_length=128)
	image = models.ImageField(upload_to='media/cache', default='static/images/dogDefault.png')


	def __unicode__(self):
		return str(self.id)

class PastFoodDog(models.Model):
	dog = models.ForeignKey(Dog)
	food = models.TextField(blank=False)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return str(self.id) + food

from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User

class UserProfile(models.Model):
	user = models.ForeignKey(User)
	name = models.CharField(blank=True, max_length=128)
	phone = models.CharField(blank=True, max_length=10)
	vet = models.CharField(blank=True, max_length=128)
	vet_update = models.DateTimeField(blank=True)
	address = models.TextField(blank=True)
	referral_taken = models.BooleanField(default=False)
	no_of_referred_users = models.IntegerField(default=0)
	user_credit = models.DecimalField(max_digits=8, decimal_places=3, default=0)

	def __unicode__(self):
		return str(self.user)

class Dog(models.Model):
	owner = models.ForeignKey(User)
	name = models.CharField(blank=False, max_length=128)
	pet = models.CharField(blank=False, max_length=3)
	breed = models.TextField(blank=False)
	age = models.CharField(blank=False, max_length=10)
	gender = models.CharField(blank=False, max_length=6)
	neutered = models.BooleanField(default=False)
	pregnant = models.BooleanField(default=False)
	pregMonths = models.IntegerField(default=0)
	lactation = models.BooleanField(default=False)
	number_of_puppies = models.IntegerField(default=0)
	weight = models.IntegerField(blank=False)
	bodyCondition = models.CharField(blank=False, max_length=128)
	activity = models.CharField(blank=False, max_length=128)
	pastfood = models.CharField(blank=True, max_length=128)
	calories = models.DecimalField(max_digits=8, decimal_places=3, default=0)

	def __unicode__(self):
		return str(self.name)

class Cat(models.Model):
	owner = models.ForeignKey(User)
	name = models.CharField(blank=False, max_length=128)
	pet = models.CharField(blank=False, max_length=3)
	breed = models.TextField(blank=False)
	age = models.CharField(blank=False, max_length=10)
	gender = models.CharField(blank=False, max_length=6)
	neutered = models.BooleanField(default=False)
	pregnant = models.BooleanField(default=False)
	pregMonths = models.IntegerField(default=0)
	lactation = models.BooleanField(default=False)
	number_of_puppies = models.IntegerField(default=0)
	weight = models.IntegerField(blank=False)
	bodyCondition = models.CharField(blank=False, max_length=128)
	activity = models.CharField(blank=False, max_length=128)
	pastfood = models.CharField(blank=True, max_length=128)
	calories = models.DecimalField(max_digits=8, decimal_places=3, default=0)

	def __unicode__(self):
		return str(self.id)

class ReferralCode(models.Model):
	user = models.ForeignKey(User)
	code = models.CharField(blank=False, max_length=128, unique=True)

	def __unicode__(self):
		return self.code

class Vet(models.Model):
	user = models.ForeignKey(User)
	name = models.CharField(blank=True, max_length=128)
	phone = models.CharField(blank=True, max_length=10)
	code = models.CharField(unique=True, blank=True, max_length=128)
	address = models.TextField(blank=True)
	no_of_referred_users = models.IntegerField(default=0)
	user_credit = models.DecimalField(max_digits=8, decimal_places=3, default=0)

	def __unicode__(self):
		return str(self.name)
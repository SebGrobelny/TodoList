# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

import datetime 

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager

#using the builtin Django user since Basic Authentication is being used and the specs are already present in this builtin
class MyUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            first_name=first_name,
            last_name=last_name,
            password=password,

        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )

    #registered users become active users
    is_active = models.BooleanField(default=True)
    #but still have dont have access to admin privileges
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name']

    def get_username(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):

        return self.first_name

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

class TodoList(models.Model): #definition for list model
  title = models.CharField(max_length=250,default=None) 
  user=models.ForeignKey(MyUser,on_delete=models.CASCADE, null=False)


  def __str__(self): 
    return self.title 
  #if queried order by title
  class Meta: 
    ordering = ['title'] 
  # #use default admin settings
  class Admin: 
    pass


class TodoItem(models.Model): 
  title = models.CharField(max_length=250) 
  #links to list
  todo_list = models.ForeignKey(TodoList,on_delete=models.CASCADE, null=False) 

  def __str__(self): 
    return self.title 
  #order by title 
  class Meta: 
    ordering = ['title'] 
  class Admin: 
    pass
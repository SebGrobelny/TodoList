# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.shortcuts import render,redirect
from django import forms

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.http import Http404
#from django.contrib.auth.models import User
from models import MyUser, TodoList, TodoItem
from forms import UserCreationForm

import base64

#HTTP basic auth
from decorators import HTTP_login_required

def register(request):

    status_code = 302
    if request.method == 'POST':
        form=UserCreationForm(request.POST)

        if form.is_valid():

            user= form.save()
            status = 204
            template_name = 'create_list.html'

            # login(request, user)
            status_code = 204
            data ={'state':"Congratulations you have created a user feel free to create a list by visiting /list/"}

            return HttpResponse(status=status_code)

        else:
            
            status_code = 401
            data = {'state':"A user with those credentials already exists"}

    else:
        form = UserCreationForm()
        data = {'form': form}

    return render(request,template_name='register.html',context=data,status=status_code)


@csrf_protect
def login_view(request):

    state="Please log in..."
    status_no=500

    if request.method=='POST':
        user = authenticate(email=request.POST.get('email'),password=request.POST.get('password'))

        if user:
            login(request,user)

            state = "You're successfully logged in!"

            next = request.GET.get('next')
            if next:

                return HttpResponseRedirect(next)
            else:

                status_no = 204
                content = "User has successfully logged in"
                return HttpResponseRedirect('/list')
                #return render(request,'success.html',status=status_no)
        else:
            state = "User credentials are invalid"
            status_no=401



    data={'state':state}
    
    return render(request,'index.html',context=data,status=status_no)

def logout_view(request):

    logout(request)


    content = "User has been logged out"

    return HttpResponse(content, status=401)

@login_required
def home_page(request):
    #finding the right user and corresponding list objects to display based on the user id in the session
    user_obj = request.user

    list_obj=TodoList.objects.filter(user=user_obj)

    # for key in list_obj:
    #     print key
    # print list_obj
    data = {'Name':user_obj,'List':list_obj}
    return render(request,'home.html',data)



@login_required
def create_list(request):
    #list creation
    # for key in request.session.keys():
    #     print key
    #     print request.session[key]
    # MyUser.objects.filter(id=request.user).get()
    user_obj= request.user
    if request.method=='POST':

        list_obj=TodoList(title=request.POST.get('title'),user=user_obj)

        list_obj.save()

        #Response 
        body = {'list_id': list_obj.id, 'list_name':list_obj.title}
        status_code = 200

        return HttpResponse(content= json.dumps(body), status=status_code, content_type="application/json")


    data={'Name': user_obj}



    return render(request,template_name='create_list.html',context=data)


@login_required
def list_item(request,list_id):

    status_code = 200
    user_obj=request.user

    #find TodoList with list_id if exists
    try:
        list_obj=TodoList.objects.filter(id=list_id).get()
        todo_obj=TodoItem.objects.filter(todo_list=list_id)

    #TodoList is not found
    except TodoList.DoesNotExist:
        status_code = 404
        return HttpResponse(status=status_code)


    #method for adding item to list
    if request.POST.get('_method') == 'post':
        todo_obj = TodoItem(title=request.POST.get('todo_item_name'), todo_list= list_obj)
        todo_obj.save()

        body = {'todo_item_id': todo_obj.id, 'todo_item_name':todo_obj.title}
        status_code = 200

        return HttpResponse(content= json.dumps(body), status=status_code, content_type="application/json")



    #method for deleting
    elif request.POST.get('_method') == 'delete' or request.method == 'DELETE':

        list_obj.delete()
        status_code = 204
        return HttpResponse(status=status_code)


    #method for viewing the response object in the tests
    elif request.GET.get('_method') == 'get':
        # list_obj = TodoList.objects.filter(id=list_id)
        # todo_obj = TodoItem.objects.filter(todo_list=list_obj)

        status_code = 200
        body = []

        if todo_obj:
            for todo in todo_obj:
                hash_map = {}
                hash_map['list_item_name'] =  todo.title
                hash_map['list_item_id'] = todo.id

                body.append(hash_map)


        return HttpResponse(content= json.dumps(body), status=status_code, content_type="application/json")

    #method for viewing on template

    data={'Name': user_obj,'list':list_obj, 'todo':todo_obj}

    return render(request,template_name='list_item.html',context=data,status=status_code)



@login_required
def todo_item(request,list_id,todo_id):

    # print list_id
    # print todo_id
    # print request.method
    user_obj=request.user

    try:
        list_obj=TodoList.objects.filter(id=list_id).get()

        #try to find todo item with matching id 
        try:                 
            todo_obj=TodoItem.objects.filter(todo_list=list_id).get(id=todo_id)

        #TodoItem is not found
        except TodoItem.DoesNotExist:
            status_code = 404
            return HttpResponse(status=status_code)

    #TodoList is not found
    except TodoList.DoesNotExist:
        status_code = 404

        return HttpResponse(status=status_code)


    #method for editing todo item in list
    if request.POST.get('_method') == 'put' or request.method == 'PUT':
        
        todo_obj = TodoItem(title=request.POST.get('todo_item_name'), id=todo_id, todo_list= list_obj)
        todo_obj.save()
        body={'todo_item_id':todo_obj.id,'todo_item_name':todo_obj.title} 

        status_code = 200
        return HttpResponse(content= json.dumps(body), status=status_code, content_type="application/json")


    #method for deleting --
    elif request.POST.get('_method') == 'delete' or request.method == 'DELETE':

        todo_obj.delete()
        status_code = 204

        return HttpResponse(status=status_code)

    else:
        
        data={'Name': user_obj,'todo':todo_obj}

        return render(request,template_name='todo_item.html',context=data)




# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.contrib.auth.models import AnonymousUser 

# Create your tests here.
# from django.contrib.auth.models import AnonymousUser, User
from models import MyUser, TodoList, TodoItem
from django.test import TestCase, RequestFactory

from views import create_list, list_item, todo_item

#Unit tests for all the GET POST PUT DELETE requests made to the server
class TestModels(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create_user(
             email='simpletest@gmail.coom', first_name='Simple', last_name='Test', password='top_secret')
        self.list = TodoList(title="Test Todo 1",user=self.user)
        self.list.save()


    def test_check_list(self):

        #ensure that type of list is TodoList
        self.assertTrue(isinstance(self.list, TodoList))
        #check that the list was correctly created
        self.assertTrue(self.list.title,"Test Todo 1")

    def test_create_todo(self):

        todo_obj = TodoItem(title="Todo 1", todo_list=self.list)
        todo_obj.save()

        #checking type of TodoItem that was just created
        self.assertTrue(isinstance(todo_obj, TodoItem))
        #checking title and ensuring that it is correctl associated with todo_list
        self.assertEqual(todo_obj.title, "Todo 1")
        self.assertEqual(todo_obj.todo_list, self.list)

    def test_edit_todo(self):
        #call create to avoid rewriting creation logic
        self.test_create_todo()

        todo_obj = TodoItem.objects.filter(todo_list=self.list).get()
        old_id = todo_obj.id

        todo_obj = TodoItem(title="Different Todo", id=todo_obj.id, todo_list=self.list)
        todo_obj.save()

        #search for the TodoItem again
        todo_obj = TodoItem.objects.filter(todo_list=self.list).get()

        #verify that TodoItem is now named differently
        self.assertEqual(todo_obj.title, "Different Todo")

        #verify that this is in fact the Todo Item we created before
        self.assertEqual(todo_obj.id, old_id)

    def test_delete_todo(self):
        #call create to avoid rewriting creation logic
        self.test_create_todo()

        todo_obj = TodoItem.objects.filter(todo_list=self.list)
        todo_obj.delete()
        #verify that TodoItem is no longer there
        self.assertEqual(len(todo_obj), 0)

    def test_delete_list(self):
        list_obj = TodoList.objects.filter(id=self.list.id)
        list_obj.delete()

        self.assertEqual(len(list_obj),0)

        

#Unit tests for all the GET POST PUT DELETE requests made to the server
class TestViews(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

        #user and list to be used throughout tests
        self.user = MyUser.objects.create_user(
             email='simpletest@gmail.coom', first_name='Simple', last_name='Test', password='top_secret')
        self.list = TodoList(title="Test Todo 1", user=self.user)


    def test_get_list(self):
        
        # Create an instance of a GET request.
        request = self.factory.get('/list')

        request.user = self.user

        # Test create_list deployed at '/list'
        response = create_list(request)
        
        # Test to see that we can GET the view
        self.assertEqual(response.status_code, 200)

    def test_create_list(self):
        #method to check for list creation
        request = self.factory.post('/list',{'title':self.list.title})
        request.user = self.user

        response = create_list(request)
        # print response.content
        # print response.status_code
        self.assertEqual(response.content, '{"list_name": "Test Todo 1", "list_id": 1}')
        self.assertEqual(response.status_code, 200)

        #check for an empty list of hashmaps since there are currently no todos
        request = self.factory.get('/list/1', {'_method':'get'})
        request.user = self.user

        response = list_item(request,1)
        self.assertEqual(response.content, '[]')
        self.assertEqual(response.status_code, 200)

        request = self.factory.get('/list/1/1')
        request.user = self.user
        response = todo_item(request,1,1)
        self.assertEqual(response.status_code, 404)


    def test_create_lists(self):
        self.test_create_list()


        for i in range(2,30):
            request = self.factory.post('/list',{'title':"Test Todo "+str(i)})
            request.user = self.user

            response = create_list(request)
            # print response.content
            # print response.status_code
            self.assertEqual(response.content, '{"list_name": "Test Todo '+str(i)+'", "list_id": '+str(i)+'}')
            self.assertEqual(response.status_code, 200)

            #check for an empty list of hashmaps since there are currently no todos
            request = self.factory.get('/list/'+str(i), {'_method':'get'})
            request.user = self.user

            response = list_item(request,1)
            self.assertEqual(response.content, '[]')
            self.assertEqual(response.status_code, 200)

            request = self.factory.get('/list/'+str(i)+'/1')
            request.user = self.user
            response = todo_item(request,1,1)
            self.assertEqual(response.status_code, 404)

  



    def test_post_todos(self,num=30):

        #create list
        self.test_create_list()

        #create a few TodoItems via post to /list/{{id}} and check that endpoints return 200 status and body

        #list of hashmaps we will append to 
        hashmap_list = []
        #create 100 todos stored under the list
        for i in range(1,num):
            #the dictionary we will use to pass 
            request_dict = {}
            request_dict['_method'] = 'post'
            request_dict['todo_item_name'] = 'Todo item '+str(i)
            request = self.factory.post('/list/1', request_dict)
            request.user = self.user

            response = list_item(request,1)
            #conversion from string to json object
            response_dict = json.loads(response.content)

            self.assertEqual(response_dict["todo_item_id"], i)
            self.assertEqual(response_dict["todo_item_name"], "Todo item "+str(i))
            self.assertEqual(response.status_code, 200)

            request_dict = {}
            request_dict['_method'] = 'get'

            request = self.factory.get('/list/1', request_dict)
            request.user = self.user




            response = list_item(request,1)
            response_list = json.loads(response.content)
            
            response_dict = {}
            response_dict['list_item_name'] = "Todo item "+str(i)
            response_dict['list_item_id'] = i
            hashmap_list.append(response_dict)

            #check to see that the length of the response (amount of TodoItems currently associated with the TodoList) is the same as
            #the number of TodoItems we have posted
            self.assertEqual(len(response_list), len(hashmap_list))
            self.assertEqual(response.status_code, 200)



    def test_edit_todo(self):
        self.test_post_todos(3)
        #testing put todo_item
        request = self.factory.post('/list/1/1', {'_method':'put', 'todo_item_name': 'New name item 1'})
        request.user = self.user

        response = todo_item(request,1,1)
        self.assertEqual(response.content, '{"todo_item_name": "New name item 1", "todo_item_id": 1}')
        self.assertEqual(response.status_code, 200)

        #testing delete todo_item
        request = self.factory.post('/list/1/1', {'_method':'delete'})
        request.user = self.user

        response = todo_item(request,1,1)
        self.assertEqual(response.status_code, 204)

        #check to ensure that item is no longer there
        request = self.factory.get('/list/1/1')
        request.user = self.user

        response = todo_item(request,1,1)
        self.assertEqual(response.status_code, 404)

    def test_delete_list(self):
        self.test_create_list()
        request = self.factory.post('/list/1', {'_method':'delete'})
        request.user = self.user

        response = list_item(request,1)
        self.assertEqual(response.status_code, 204)

        #check to ensure that item is no longer there
        request = self.factory.get('/list/1')
        request.user = self.user

        response = list_item(request,1)
        self.assertEqual(response.status_code, 404)







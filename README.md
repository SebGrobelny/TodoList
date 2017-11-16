Todo List App
=================
 
Welcome to Sebastian Grobelny's TodoList app in Django!

Table of contents
=================

  * [Todo List App](#todo-list-app)
  * [Table of contents](#table-of-contents)
  * [Installation](#installation)
  * [How to Run](#how-to-run)
  * [Design](#design)
    * [Framework Choice](#framework-choice)
    * [models](#models)
    * [views](#views)
    * [decorators](#views)
  * [Testing](#testing)
  	* [tests](#tests)


 
Installation
============
For this project I used Django 1.11, please ensure that is the version of django that you have installed on your commandline before attempting to run the application
```
pip install Django==1.11.7

```
 
 
 
How to Run
==========

Running the website from the commandline within the root directory /todo_rest.
```
python manage.py runserver
```
Running my test scripts for the views and models set up in my tests.py also from the commandline in /todo_rest. 

```
python manage.py test
```

Design
======

Framework Choice
----------------
I chose to build the application in Django due largely to my familiarity with it for creating server-side aplications. Since the project required creating an API client in Python, I immediately decided to associate the endpoints provided with views, and the user, todo list and todo item storage in models as would be typical in a Django application. Django's templating language also made it easy to render my responses unto whatever template I was using. I was thinking of Flask but even though setting up the server itself would be easy, Flask lacks the builtin database connections which were crucial towards maintaining the models I built for users and todo lists with their todo items.

models
------
Found in todo_rest/todo_list/models.py, I built three models for this project: a TodoList, TodoItem, MyUser and accompanying MyUserManager. The MyUser model is one that I simply extended from Django's builtin User model found in django.contrib.auth. The MyUser model differs from the typical User model in using email as a substitute for username, since this was a project requirement. The MyUser model also accepts first name, last name and password as required by the specifications in the project making those the attributes that now populate the builtin Django User model. I had to setup the corresponding MyUserManager to provide Django with the logic that I wanted in place during new user creation, namely to accept those parameteres I mentioned before in the create_user() method. The TodoList model has a title, and user attribute. The title is just the title of the TodoList object created by the user but the user attribute is actually a foreign key that associates the given TodoList to a MyUser instance. Doing this was necessary as each user had to get associated with their TodoLists, the foreign key made this possible as this would later be a query parameter in the list view as the user associated with the session would get passed in to find their lists. The TodoItem also has a title attribute but also has a todo_list instance. The todo_list instance is a foreign key to the TodoList under which the TodoItem was filed and again to associate TodoItems with their given TodoList in queries to the models.

forms
-----
Found in todo_rest/todo_list/forms.py, the only form I built out was the UserCreationForm which gets rendered to the register.html template upon accessing the '/register' endpoint. It accepts first_name, last_name, email and password which then get associated with a user thanks to the form's save method which ends up calling create_user. I also provided an authenticate_via_email method which checks to see if the email entered on the form is one already in use on the site. Since the specification required that emails by unique to each user this will actually cause the form to be invalid prompting for new credentials.The alternative here was of course to use serializers but since I wanted to make the application as user friendly as possible I opted for the form since it can easily be rendered unto an HTML template.


views
-----

My views or endpoints are found in todo_rest/todo_list/views.py.

### register

Tackling the '/register', this view supplies the UserCreationForm to the template if the request.method is not POST. If the request.method is POST, the user has attempted to submit the form then we check to see if the form is valid using the criteria mentioned in forms.py. If it is valid we choose to save the form and hence the user to the Djanog user model, returning a 204 status code. If it is not valid a message gets stored in state which then gets rendered unto the template indicating what went wrong with the registration.

### login_view

An added endpoint at '/login', this is an extension of the defualt Django login, since Django authentication is Session Authentication by default it associates the session with the user if there credentials are valid. The main reason I supplied this was to make use of the @login_required decorator which I place above every view besides register, login_view, and logout_view to authenticate the user before granting them access to the view. 

### logout_view

An added endpoint at '/logout', this is an Extension of the default Django logout, namely to allow the user to click logout and potentially login as a different user. This was a feataure I wanted in the application and something I was not able to accomplish using HTTP Basic Auth which I discuss in decorators.py. 

### home

An added endpoint at '/', I did this to allow the logged in user to see and have access to all of the TodoLists that they have created. All the view does is query the TodoList model given the current authenticated user and stores the QuerySet of TodoLists along with the authenticated user into a dictionary. Each of the lists is hyperlinked to their corresponding '/list/{{id}}' endpoint in the template itself.

### create_list

Tackling the '/list' endpoint, this view supplies a template allowing users to fill out the desired title they want to create the TodoList with. This gets submitted through an HTML form with a POST method header. 

##### POST
When the user fills out the input field and hits the post button, the view catches the POST request and creates a new TodoList with the given title and user before returning the dictionary with the 'list_id'  and 'list_name' of the created TodoList along with a 200 status code.

### list_item

Tackling the '/list/{{id}}',  this view queries for the TodoList given id and checks for its existence raising a 404 status code if not found. Also queries for the corresponding TodoItem given the TodoList as a paramater and stores these results along with the TodoList unto the template. The template provides an input field that allows users to supply a TodoItem title which can be submitted by clicking post, and buttons for Delete and Get. I provided a sort of hack given that Django does not support PUT and Delete by specifiying a _method in the form to be either Post, Put or Delete since the method used for all three was POST. The GET method by default returns the template so I added another _method for tackling the 'View list' spec.
##### POST
When the user fills out the input field and hits the post button, the view identifies the _method as a post. The 'Add to List' spec is tackled as the view takes whats in the input field and creates a TodoItem object using the input field contents as the title and id as the foreign key to the TodoList. The TodoItem is saved and a 200 status code is outputted. 
##### DELETE
If the Delete button is pressed then the _method provided is delete and the 'Delete List' is tackled as the TodoList at id is deleted from the model returning a 204 status code. 
##### GET
If the Get button is pressed then the _method provided is get and the required 'View List' directive is handled returning the expected list of hashmaps with list_item_name and list_item_id of the TodoItems stored under the TodoList with id along with a 200 status code.

### todo_item

Tackling the '/list/{{id}}/{{todo_id}}', this view queries for the TodoItem given the todo_id from the TodoList with id if this item does not exist a 404 status code is raised. The view provides a dictionary of the todo_item for view in the template and an input field allowing the user to edit the TodoItem title present at todo_id.The approach from list_item is again used for Put and Delete requests. 

##### PUT
If input field is filled out and the put button is hit the _method passed to the view is put and the required 'Update Item in List' is tackled.The view creates a TodoItem with title from the input field and id from todo_id in order to effectively replace the TodoItem currently present at todo_id. The view then stores the TodoItem credentials into a dictionary response with status_code 200.
##### DELETE
If the delete method is pushed then the _method passed to the view is delete, and the 'Delete item in list directive is handled'. The TodoItem found under todo_id in TodoList at id is deleted from the model and a 204 status code is outputted.



decorators
----------
Found in todo_rest/todo_list/decorators.py this tackles the HTTP Basic Auth requirement of the project but is not currently in use. The reason for this is based on my research HTTP Basic has no clear defined method for logging a user out besides closing the browser out completely. I originally used this implemented decorator in this file called @HTTP_login_required before every view in my views.py. This would prompt the browser window for login and would authenticate a user if they were found in the Django user models, but I could not find a way to log a user out with this authentication scheme. This can be easily added back in by using this decorator instead of the @login_required decorator currently in use, but I wanted to have the application log people in and log people out at their choosing so the current Authentication Scheme is the default one used by Django which is powered by SessionMiddleware and AuthenticaitonMiddleware. 

Testing
=======

tests
-----
Found in todo_rest/todo_list/tests.py the TestModels test cases mimic the API behaviour without actually connecting to the server. The methods test for TodoList creation, and deletion along with TodoItem creation, update and deletion using the models I built without the endpoints in views.py. The TestViews test cases test the actual API endpoints as the cases put in requests and validate the responses when creating, deleting and updating TodoList and TodoItem models.







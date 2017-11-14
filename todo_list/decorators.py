from django.http import HttpResponse
from django.contrib.auth import authenticate,login
import base64
from django.shortcuts import render_to_response

def HTTP_login_required(f):

    def HTTP_login(request):

            if 'HTTP_AUTHORIZATION' in request.META:

                    print request.META

                    auth = request.META['HTTP_AUTHORIZATION'].split()

                    if len(auth) == 2:

                        if auth[0].lower() == "basic":
                                email, password = base64.b64decode(auth[1]).split(':', 1)
                                print "in authorization"
                                print email
                                print password
                                user = authenticate(email=email, password=password)
                                print user

                                if user is not None and user.is_active:
                                      print "initial request"
                                      print request
                                      print
                                      login(request, user)
                                      print "final request"
                                      print request 
                                      print
                                      return render_to_response('create_list.html')


            # otherwise ask for authentification
            response = HttpResponse("")
            response.status_code = 401
            response['WWW-Authenticate'] = 'Basic realm="restricted area"'
            return response

    HTTP_login.__doc__=f.__doc__
    HTTP_login.__name__=f.__name__
    return HTTP_login


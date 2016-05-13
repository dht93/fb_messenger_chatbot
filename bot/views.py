from django.views import generic
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json, requests, random, re
from pprint import pprint
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
import textwrap

PAGE_ACCESS_TOKEN = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
VERIFY_TOKEN = "XXXXXXXXXXXXXXXXX"


def post_facebook_message(fbid, recevied_message):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":recevied_message}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    pprint(status.json())

def get_info(title):
    base_url = "http://www.omdbapi.com/"
    querystring = {"t":title,"plot":"short","tomatoes":"true"}
    response = requests.request("GET", base_url, params=querystring)
    # pprint (response.text)
    details = json.loads(response.text)
    return details

class BotView(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token']== 'XXXXXXXXXXXXXXX':
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    #this is to exempt crsf token which is required by django by default
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        pprint(incoming_message)
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                if 'message' in message:
                    print message['message']['text']
                    movie_details = get_info(message['message']['text'])
                    response_text = 'Title: '+ movie_details['Title']
                    for field in ['Director', 'Plot', 'tomatoMeter', 'tomatoConsensus']:
                        if not movie_details.get(field, -1) == -1:
                            response_text += '\n' + field + ': ' + str(movie_details[field])+'\n'
                    lst_of_response_msgs = textwrap.wrap(response_text, 314)
                    if len(lst_of_response_msgs)>1:
                        for i in range(len(lst_of_response_msgs)):
                            if i==0:
                                msg = lst_of_response_msgs[i]+'...'
                            elif i==len(lst_of_response_msgs)-1:
                                msg = '...' + lst_of_response_msgs[i]
                            else:
                                msg = '...'+ lst_of_response_msgs[i] + '...'
                            post_facebook_message(message['sender']['id'], msg)
                    else:
                        post_facebook_message(message['sender']['id'], lst_of_response_msgs[0])
                    # for field in movie_details:
                    #     post_facebook_message(message['sender']['id'], movie_details[field])
        return HttpResponse()

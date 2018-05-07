from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

# Create your views here.


# @csrf_protect
def post_listener(request):
    context = {'data': request.POST}
    print(context)
    return render(request, 'sourcetool/seepost.html', context)

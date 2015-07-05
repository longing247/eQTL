from django.shortcuts import render

# Create your views here.
def aboutView(request):
    if request.method=='GET':
        return render(request,'about/about.html',{'user':request.user})
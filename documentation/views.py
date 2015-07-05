from django.shortcuts import render

# Create your views here.
def docView(request):
    if request.method=='GET':
        return render(request,'documentation/documentation.html',{'user':request.user})
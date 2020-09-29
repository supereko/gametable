from django.shortcuts import render

def index(request):
    context = {
        'page_title': 'Игры',
        'basket': get_basket(request)
    }
    return render(request, 'authapp/login.html', context)

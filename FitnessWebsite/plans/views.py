from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import FitnessPlan
from django.contrib import auth
from django.contrib.auth.decorators import login_required
import stripe

stripe.api_key = 'sk_test_51HJhEkBx0yfTfeVyNBVW5NYtn79kqjLrfFCZYtTyTjrR6kYz779aGWoVocUR65kZf8WATnuHagDLGuzBwLsJp3jA00XIuOU2OB'

# Create your views here.
def login(request):
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST['username'],password=request.POST['password'])
        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            try:
                user = User.objects.get(username=request.POST['username'])
                if user:
                    return render(request, 'registration/login.html',{'error':'Incorrect Password'})
            except:
                return render(request, 'registration/login.html',{'error':'Incorrect Username'})    

    else:
        return render(request,'registration/login.html')    

def register(request): 
    if request.method == 'POST':
        if request.POST['username'] != '' and request.POST['email'] != '' and request.POST['password'] != '':
            if len(request.POST['username']) < 6:
                return render(request,'registration/signup.html',{'error':'Username Must be More 6 Characters or more'})
            elif len(request.POST['password']) < 6:
                return render(request,'registration/signup.html',{'error':'Password Must be More 6 Characters or more'})    
            else:
                user = User()
                user.username = request.POST['username']
                user.set_password(request.POST['username'])
                user.email = request.POST['email']
                try:
                    user.save()
                    return redirect('login')
                except:
                    return render(request,'registration/signup.html',{'error':'Unable to Register'})        

        else:
            return render(request,'registration/signup.html',{'error':'Fill Up All Fields'})        
    else:    
        return render(request,'registration/signup.html')

def home(request):
    plans = FitnessPlan.objects.all()
    return render(request,'plans/home.html',{'plans':plans})

def join(request):
    return render(request,'plans/join.html')

def plan(request,pk):
    plan = get_object_or_404(FitnessPlan, pk=pk)
    if plan.premium :
        return redirect('join')
    else:
        return render(request, 'plans/plan.html', {'plan':plan})

@login_required(login_url='login')
def checkout(request):

    coupons = {'newyear':20, 'dashain':20, 'tihar':20, 'anniversary':30}

    if request.method == 'POST':
        return redirect('home')
    else:    
        plan = 'monthly'
        coupon = 'none'
        price = 1000
        og_dollar = 10
        coupon_dollar = 0
        final_dollar = 10
        if request.method == 'GET' and 'plan' in request.GET:
            if request.GET['plan'] == 'yearly':
                plan = 'yearly'
                price = 10000
                og_dollar = 100
                final_dollar = 100

        if request.method == 'GET' and 'coupon' in request.GET:
            if request.GET['coupon'].lower() in coupons:
                coupon = request.GET['coupon'].lower()
                percentage = coupons[coupon]
                coupon_price = int((percentage / 100) * price)
                price = price - coupon_price
                coupon_dollar = str(coupon_price)[:-2] + '.' + str(coupon_price)[-2:]
                final_dollar = str(price)[:-2] + '.' + str(price)[-2:]

        return render(request, 'plans/checkout.html', {'plan':plan,'coupon':coupon,'price':price,
        'og_dollar':og_dollar,'coupon_dollar':coupon_dollar,'final_dollar':final_dollar})

@login_required(login_url='login')
def setting(request):
    return render(request, 'registration/settings.html') 

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('home')
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import FitnessPlan, Customer
from django.contrib import auth
from django.contrib.auth.decorators import login_required, user_passes_test
import stripe
from django.http import HttpResponse

stripe.api_key = 'sk_test_51HJhEkBx0yfTfeVyNBVW5NYtn79kqjLrfFCZYtTyTjrR6kYz779aGWoVocUR65kZf8WATnuHagDLGuzBwLsJp3jA00XIuOU2OB'

# Create your views here.
@user_passes_test(lambda u: u.is_superuser)
def updateaccount(request):
    customers = Customer.objects.all()
    for customer in customers:
        subscription = stripe.Subscription.retrieve(customer.stripe_subscription_id)
        if subscription.status != 'active':
            customer.membership = False
        else:
            customer.membership = True
        customer.cancel_at_period_end = subscription.cancel_at_period_end
        customer.save() 
        return HttpResponse('Action Completed')       


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
        if request.user.is_authenticated:
            try:
                if request.user.customer.membership:
                    return render(request, 'plans/plan.html', {'plan':plan})
            except Customer.DoesNotExist:
                return redirect('join')
        return redirect('join')
    else:
        return render(request, 'plans/plan.html', {'plan':plan})

@login_required(login_url='login')
def checkout(request):

    try:
        if request.user.customer.membership:
            return redirect('setting')
    except Customer.DoesNotExist:
        pass

    coupons = {'newyear':20, 'dashain':20, 'tihar':20, 'anniversary':30}

    if request.method == 'POST':
        stripe_customer = stripe.Customer.create(email=request.user.email, source=request.POST['stripeToken'])
        plan = 'price_1HK3n0Bx0yfTfeVyV4boDCRh'
        if request.POST['plan'] == 'yearly':
            plan = 'price_1HK3n0Bx0yfTfeVyf3wJnzk5'
        if request.POST['coupon'] in coupons:
            percentage = coupons[request.POST['coupon'].lower()]
            try:
                coupon = stripe.Coupon.create(duration='once', id=request.POST['coupon'].lower(),
                percent_off=percentage)  
            except:
                pass
            subscription = stripe.Subscription.create(customer=stripe_customer.id,
            items=[{'plan':plan}], coupon = request.POST['coupon'].lower())
        else:
            subscription = stripe.Subscription.create(customer=stripe_customer.id,
            items=[{'plan':plan}])

        customer = Customer()
        customer.user = request.user
        customer.stripe_id = stripe_customer.id
        customer.membership = True
        customer.cancel_at_period_end = False
        customer.stripe_subscription_id = subscription.id
        customer.save()    
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
    membership = False
    cancel_at_period_end = False
    if request.method == 'POST':
        subscription = stripe.Subscription.retrieve(request.user.customer.stripe_subscription_id)
        subscription.cancel_at_period_end = True
        request.user.customer.cancel_at_period_end = True
        cancel_at_period_end = True
        subscription.save()
        request.user.customer.save()
    else:
        try:
            if request.user.customer.membership:
                membership = True
            if request.user.customer.cancel_at_period_end:
                cancel_at_period_end = True
        except Customer.DoesNotExist:
            membership = False                
    return render(request, 'registration/settings.html',{'membership':membership,
    'cancel_at_period_end':cancel_at_period_end}) 

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('home')

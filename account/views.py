from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import Group
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from .decorators import allowed_users
from .forms import UpdatePhotoForm, IdentityForm, AddressForm, ProveForm
from .models import Currency, User, TradingPlan, Deposite, MiningPlan, CopiedTrade, ContractPaymentMethod, TakeTrade, Withdrawal
from super.models import Role, Trader, NewCoin, Crypto, Forex, StockList
from datetime import datetime
import pytz
import requests
from .functions import activateEmail, telegram
from .tokens import account_activation_token


# Create your views here.

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def home(request):
    copied_trade = len(CopiedTrade.objects.filter(user=request.user))
    allTrade = TakeTrade.objects.filter(user=request.user)
    for i in allTrade.values():
        current_datetime = datetime.now()
        date_datetime = i.get('expire_time')

        date_datetime = date_datetime.replace(tzinfo=pytz.utc)
        current_datetime = current_datetime.replace(tzinfo=pytz.utc)
        print(current_datetime, date_datetime)
        if current_datetime >= date_datetime and i.get('open_trade'):
            TakeTrade.objects.filter(id=i.get('id')).update(open_trade=False)
            balance = float(request.user.user_balance)
            print(balance, i.get('profit'))
            User.objects.filter(username=request.user.username).update(user_balance = float(i.get('profit')) + balance)
        else:
            continue
    openTrades = TakeTrade.objects.filter(user=request.user, open_trade=True)
    
    closeTrades = TakeTrade.objects.filter(user=request.user, open_trade=False)
    context = {
        'trade': copied_trade,
        'open' : openTrades,
        'close' : closeTrades,
    }
    return render(request, 'account/home.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def pricing(request):
    context = {}
    return render(request, 'account/pricing.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def market(request):
    market = NewCoin.objects.all()
    # market = Crypto.objects.all()
    if request.method == 'POST':
        coin = request.POST.get('coin')
        if coin == 'crypto':
            market = NewCoin.objects.filter(type=coin)
        elif coin == 'forex':
            market = NewCoin.objects.filter(type=coin)
        elif coin == 'stock':
            market = NewCoin.objects.filter(type=coin)
    context = {'data':market}
    return render(request, 'account/market.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def tradingRoom(request,ref,currency):
    usdurl = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=1m"
    eururl = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=eur&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=1m"
    jpyurl = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=jpy&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=1m"
    gbpurl = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=gbp&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=1m"
    cnyurl = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=cny&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=1m"
    
    usd_r = requests.get(url = usdurl)
    eur_r = requests.get(url = eururl)
    jpy_r = requests.get(url = jpyurl)
    gbp_r = requests.get(url = gbpurl)
    cny_r = requests.get(url = cnyurl)
    
    usd_data = usd_r.json()
    eur_data = eur_r.json()
    jpy_data = jpy_r.json()
    gbp_data = gbp_r.json()
    cny_data = cny_r.json()
    
    coin = NewCoin.objects.get(code=ref)
    context = {
        'coin':coin,
        'usd':usd_data,
        'eur':eur_data,
        'jpy':jpy_data,
        'gbp':gbp_data,
        'cny':cny_data,
    }
    return render(request, 'account/tradingroom.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def deposite(request,ref):
    currency = Currency.objects.all()
    plan = TradingPlan.objects.get(ref=ref)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        paymentMethod = request.POST.get('paymethod')

        payMethod = Currency.objects.get(abbr=paymentMethod)

        deposite = Deposite.objects.create(amount=amount,payment_method=payMethod,plan='Trading',user=request.user)
        return redirect('payment',deposite.ref)
    context = {'plan':plan,'currency':currency}
    return render(request, 'account/deposite.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def depositeMining(request,ref):
    currency = Currency.objects.all()
    plan = MiningPlan.objects.get(ref=ref)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        paymentMethod = request.POST.get('paymethod')
        getplan = request.POST.get('mining')

        payMethod = Currency.objects.get(abbr=paymentMethod)

        deposite = Deposite.objects.create(amount=amount,payment_method=payMethod,plan=getplan,user=request.user)
        return redirect('payment',deposite.ref)
    context = {'plan':plan,'currency':currency}
    return render(request, 'account/depositemining.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def payment(request,ref):
    payment = Deposite.objects.get(ref=ref)
    current_datetime = datetime.now()
    date_datetime = payment.expire_time

    date_datetime = date_datetime.replace(tzinfo=pytz.utc)
    current_datetime = current_datetime.replace(tzinfo=pytz.utc)
    if current_datetime >= date_datetime and payment.expire_time != 2:
        Deposite.objects.filter(ref=ref).update(status=3)
        return redirect('payment',ref)
    if request.method == 'POST':
        return redirect('upload-prove', ref)
    context = {'plan':payment}
    return render(request, 'account/payment.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def uploadProve(request, ref):
    form = ProveForm()
    if request.method == 'POST':
        deposite = Deposite.objects.get(ref=ref)
        form = ProveForm(request.POST, request.FILES, instance=deposite)
        if form.is_valid():
            form.save()
            # Send message to admin
            getUser = Deposite.objects.get(ref=ref)
            telegram(f'Hello admin, a deposite upload has been made by {getUser.user.username}')
            messages.success(request, 'Successful')
            return redirect('depositelist')
    context = {'form':form}
    return render(request, 'account/uploadprove.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def depositeList(request):
    deposite = Deposite.objects.filter(user=request.user)
    for i in deposite.values():
        current_datetime = datetime.now()
        date_datetime = i.get('expire_time')

        date_datetime = date_datetime.replace(tzinfo=pytz.utc)
        current_datetime = current_datetime.replace(tzinfo=pytz.utc)
        if current_datetime >= date_datetime and i.get('status') != 2:
            Deposite.objects.filter(id=i.get('id')).update(status=3)
    context = {'deposite':deposite}
    return render(request, 'account/depositelist.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def account(request):
    
    context = {}
    return render(request, 'account/account.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def refferals(request):
    context = {}
    return render(request, 'account/refferals.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def withdrawals(request):
    payment = Withdrawal.objects.filter(user=request.user)
    context = {'payment':payment}
    return render(request, 'account/withdrawals.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def buy(request):
    context = {}
    return render(request, 'account/buy.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def crypto(request):
    currency = Currency.objects.all()
    if request.method == 'POST':
        amount = request.POST.get('amount')
        paymentMethod = request.POST.get('paymethod')
        plan = request.POST.get('mining')

        payMethod = Currency.objects.get(abbr=paymentMethod)

        deposite = Deposite.objects.create(amount=amount,payment_method=payMethod,plan=plan,user=request.user)
        return redirect('payment',deposite.ref)
    context = {'currency':currency}
    return render(request, 'account/crypto.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def traders(request):
    traders = Trader.objects.all()
    if request.method == 'POST':
        hint = request.POST.get('hint')
        traders = Trader.objects.filter(name__contains=hint)
    copied = CopiedTrade.objects.filter(user=request.user)
    context = {'traders':traders,'copied':copied}
    return render(request, 'account/traders.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def copyTrade(request, ref):
    trader = Trader.objects.get(ref=ref)
    if CopiedTrade.objects.filter(trade=trader,user=request.user).exists():
        messages.warning(request, 'Trade already copied')
        return redirect('traders')
    CopiedTrade.objects.create(trade=trader,user=request.user,pending=True)
    getUser = CopiedTrade.objects.get(trade=trader,user=request.user).user.username
    # Send message to admin
    telegram(f'Hello admin, {getUser} just copied a trade',)
    return redirect('traders')

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def cancelTrade(request, ref):
    trade = CopiedTrade.objects.filter(ref=ref)
    # Send mail to admin
    getUser = CopiedTrade.objects.get(ref=ref)
    getTrade = Trader.objects.get(id=getUser.trade.id)
    if TakeTrade.objects.filter(trader=getTrade,user=User.objects.get(username=getUser.user.username)).exists():
        messages.warning(request, 'This trader is active')
        return redirect('traders')
    trade.delete()
    # Send message to admin
    telegram(f'Hello admin, {getUser.user.username} just cancel a trade',)
    return redirect('traders')

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def tradingPlans(request):
    plans = TradingPlan.objects.all()
    context = {'plan':plans}
    return render(request, 'account/tradingplans.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def miningPlans(request):
    plans = MiningPlan.objects.all()
    context = {'plan':plans}
    return render(request, 'account/miningplans.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def selectWithdrawal(request):
    context = {}
    return render(request, 'account/selectwithdrawal.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def updateEmail(request):
    if 'email' in request.POST:
        getUser = request.user.username
        # Send message to admin
        telegram(f'Hello admin, {getUser} is requesting for email token.')
    elif 'sub' in request.POST:
        token = request.POST.get('token')
        email1 = request.POST.get('email1')
        email2 = request.POST.get('email2')
        if token != request.user.token:
            messages.warning(request, 'incorrect token')
            return redirect('updateemail')
        else:
            if email1 == email2:
                User.objects.filter(username=request.user.username).update(email=email1)
                messages.success(request, 'Done')
                return redirect('updateemail')
            else:
                messages.warning(request, 'both email did not match')
                return redirect('updateemail')
    context = {}
    return render(request, 'account/updateemail.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def updatePhoto(request):
    user= request.user
    form = UpdatePhotoForm()
    if request.method == 'POST':
        form = UpdatePhotoForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Done')
            return redirect('updatephoto')
    context = {'form':form}
    return render(request, 'account/updatephoto.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def updatePassword(request):
    if request.method == 'POST':
        pass0 = request.POST.get('pass0')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        user = User.objects.get(username=request.user.username)
        if user.check_password(pass0):
            if pass1 == pass2:
                u = User.objects.get(username=request.user.username)
                u.set_password(pass1)
                u.psw = pass2
                u.save()
                User.objects.filter(username=request.user.username).update(password_reset=False)
                user = authenticate(request, username=request.user.username, password=pass1)
                messages.success(request, 'Password changed successfully')
                return redirect('logout')
                # if user is not None:
                #     login(request,user)
                #     return redirect('home')
            else:
                messages.warning(request, 'Password did not match')
                return redirect('updatepassword')
        else:
            messages.warning(request,'incorrect password')
            return redirect('updatepassword')
    context = {}
    return render(request, 'account/updatepassword.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def settings(request):
    context = {}
    return render(request, 'account/settings.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def profile(request):
    context = {}
    return render(request, 'account/profile.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def notifications(request):
    context = {}
    return render(request, 'account/notifications.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def updateAddress(request):
    if request.method == 'POST':
        street = request.POST.get('street')
        post = request.POST.get('post')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        
        User.objects.filter(username=request.user.username).update(street_address=street, post_code=post, city=city, state=state, country=country)
        messages.success(request,'Profile updated')
        return redirect('profile')
    context = {}
    return render(request, 'account/updateaddress.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def verification(request):
    context = {}
    return render(request, 'account/verification.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def identity(request):
    client = request.user
    form = IdentityForm()
    if request.method == 'POST':
        form = IdentityForm(request.POST, request.FILES, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account updated')
            return redirect('identity')
    context = {'form':form}
    return render(request, 'account/identity.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def address(request):
    client = request.user
    form = AddressForm()
    if request.method == 'POST':
        form = AddressForm(request.POST, request.FILES, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account updated')
            return redirect('address')
    context = {'form':form}
    return render(request, 'account/address.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def bank(request):
    if 'submit' in request.POST:
        to = request.POST.get('to')
        withdrawal = request.POST.get('withdrawal')
        bank = request.POST.get('bank')
        acct = request.POST.get('acct_name')
        amount = request.POST.get('amount')
        
        if withdrawal == request.user.withdrawal_token:
            Withdrawal.objects.create(
                amount=amount,payment_method=to,user=request.user,mode='bank',bank_name=bank,acct_name = acct
            )
            # Send message to admin
            telegram(f'Hello admin, {request.user.username} just placed a withdrawal via bank')
            
            messages.success(request, 'Done')
            return redirect('bank')
        else:
            messages.warning(request, 'Invalid withdrawal code')
            return redirect('withdrawals')
    context = {}
    return render(request, 'account/bank.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def paypal(request):
    if 'submit' in request.POST:
        to = request.POST.get('to')
        withdrawal = request.POST.get('withdrawal')
        email = request.POST.get('email')
        amount = request.POST.get('amount')
        
        if withdrawal == request.user.withdrawal_token:
            Withdrawal.objects.create(
                amount=amount,payment_method=to,user=request.user,mode='paypal',paypal_email=email
            )
            # Send message to admin
            telegram(f'Hello admin, {request.user.username} just placed a withdrawal via PayPal')
            
            messages.success(request, 'Done')
            return redirect('withdrawals')
        else:
            messages.error(request, 'Invalid withdrawal code')
            return redirect('paypal')
    context = {}
    return render(request, 'account/paypal.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def cryptoWithdrawal(request):
    currency = Currency.objects.all()
    if 'submit' in request.POST:
        to = request.POST.get('to')
        withdrawal = request.POST.get('withdrawal')
        paymethod = request.POST.get('paymethod')
        address = request.POST.get('address')
        amount = request.POST.get('amount')
        
        if withdrawal == request.user.withdrawal_token:
            Withdrawal.objects.create(
                amount=amount,payment_method=paymethod,user=request.user,mode='crypto',wallet_address=address
            )
            # Send message to admin
            telegram(f'Hello admin, {request.user.username} just placed a withdrawal via crypto to {to}')
            
            messages.success(request, 'Done')
            return redirect('withdrawals')
        else:
            messages.warning(request, 'Invalid withdrawal code')
            return redirect('crypto-withdrawal')
    context = {'currency':currency}
    return render(request, 'account/cryptowithdrawal.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def cashApp(request):
    if 'submit' in request.POST:
        to = request.POST.get('to')
        withdrawal = request.POST.get('withdrawal')
        tag = request.POST.get('tag')
        amount = request.POST.get('amount')
        
        if withdrawal == request.user.withdrawal_token:
            Withdrawal.objects.create(
                amount=amount,payment_method=to,user=request.user,mode='CassApp',cashapp_tag=tag
            )
            # Send message to admin
            telegram(f'Hello admin, {request.user.username} just placed a withdrawal via cashapp')
            
            messages.success(request, 'Done')
            return redirect('withdrawals')
        else:
            messages.warning(request, 'Invalid withdrawal code')
            return redirect('cashapp')
    context = {}
    return render(request, 'account/cashapp.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def mining(request):
    context = {}
    return render(request, 'account/mining.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def contract(request):
    context = {}
    return render(request, 'account/contract.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def buyContract(request):
    pay = ContractPaymentMethod.objects.all()
    context = {'pay':pay}
    return render(request, 'account/buycontract.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def contractPayment(request, ref):
    pay = ContractPaymentMethod.objects.get(name=ref)
    context = {'pay':pay}
    return render(request, 'account/nopayment.html',context)

def loginuser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.warning(request,'username does not exist')
            return redirect('login')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            if user.password_reset:
                return redirect('password_reset',username)
            else:
                if user.role == 'admin':
                    return redirect('admin-home')
                else:
                    return redirect('home')
        else:
            messages.warning(request,'Incorrect username or password')
            return redirect('login')
    return render(request, 'account/signin.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def logoutuser(request):
    logout(request)
    return redirect('login')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        currency = request.POST.get('currency')
        
        if ' ' in username:
            messages.warning(request, 'Invalid email address')
            return redirect('login')
        
        if User.objects.filter(email=email).exists() or User.objects.filter(username=username).exists():
            messages.warning(request, 'Email or username already used')
            return redirect('login')
        
        if pass1 != pass2:
            messages.warning(request, 'Password did not match')
            return redirect('login')

        user = User.objects.create_user(username,email,pass1)
        user.is_staff = True
        user.is_active = False
        user.is_superuser = False
        user.last_name = last_name
        user.first_name = first_name
        user.currency = currency
        user.role = 'client'
        user.psw = pass1
        user.save()

        if not Group.objects.filter(name='client').exists():
            Group.objects.create(name='client')

        User.objects.filter(username = username).update(image = 'passport.jpg')
            
        userid = User.objects.get(username=username).id
        getgroup = Group.objects.get(name='client')
        getgroup.user_set.add(userid)
        
        # Activate email
        activateEmail(request, user, email)
        return redirect('login')
    content = {}
    return render(request, 'account/signup.html')

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.verify_email = True
        user.save()
        messages.success(request, 'Verification was successful')
        return redirect('login')
    else:
        messages.warning(request, 'Activation link is invalid')
    return redirect('home')
    
@login_required(login_url='login')
@allowed_users(allowed_roles=['client','super'])
def withdrawalCode(request):
    if 'withdrawal' in request.POST:
        # Send message to admin
        getUser = request.user.username
        telegram(f'Hello admin, {getUser} is requesting for withdrawal code.',)
        return redirect('home')
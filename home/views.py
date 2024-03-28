from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.conf import settings
from EC_Admin.models import Voters
from django.core.mail import send_mail
import requests

# Create your views here.
def home(request):
    return render(request, 'home.html')

def v_register(request):
    return render(request, 'voter/v_register.html')

def vregister(request):
    if (request.method == 'POST'):
        voterid_no = request.POST['vid']
        name = request.POST['name']
        father_name = request.POST['fname']
        gender = request.POST['gender']
        dateofbirth = request.POST['dob']
        address = request.POST['address']
        mobile_no = request.POST['mno']
        state = request.POST['state']
        pincode = request.POST['pincode']
        parliamentary = request.POST['ParliamentaryConstituency']
        assembly = request.POST['AssemblyConstituency']
        voter_image = request.FILES['vphoto']
        if (Voters.objects.filter(voterid_no=voterid_no).exists()):
            messages.info(request, 'voter id already registered')
            return render(request, 'voter/v_register.html')
        else:
            add_voter = Voters(voterid_no=voterid_no, name=name, father_name=father_name, gender=gender,
                               dateofbirth=dateofbirth, address=address, mobile_no=mobile_no, state=state,
                               pincode=pincode, parliamentary=parliamentary, assembly=assembly, voter_image=voter_image)
            add_voter.save()
            messages.info(request, 'voter added, please kindly complete the registration with voterid ' )
            # return render(request, 'registervid.html')
            return redirect('registervidpage')



def v_login(request):
    return render(request, 'vlogin.html')


def vlogin(request):
    if (request.method == 'POST'):
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_superuser is False:
            auth.login(request, user)
            request.session['voterid_no'] = username
            return redirect('vhome')
        else:
            messages.info(request, 'Invalid Credentials')
            return render(request, 'vlogin.html')

def admin_login(request):
    return render(request, 'adminlogin.html')

def adminlogin(request):
    if(request.method == 'POST'):
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username = username, password = password)
        if user is not None and user.is_superuser is True:
            auth.login(request, user)
            request.session['ecadmin_id'] = username
            return redirect('adminhome')
        else:
            messages.info(request, 'Invalid Credentials')
            return render(request, 'adminlogin.html')

# def login(request):
#     if (request.method == 'POST'):
#         username = request.POST['username']
#         password = request.POST['password']
#         loginas = request.POST['loginas']
#         if loginas == "voter":
#             user = auth.authenticate(username=username, password=password)
#             if user is not None and user.is_superuser is False:
#                 auth.login(request, user)
#                 request.session['voterid_no'] = username
#                 return redirect('vhome')
#             else:
#                 messages.info(request, 'Invalid Credentials')
#                 return render(request, 'index.html')
#         elif loginas == "admin":
#             user = auth.authenticate(username=username, password=password)
#             if user is not None and user.is_superuser is True:
#                 auth.login(request, user)
#                 request.session['ecadmin_id'] = username
#                 return redirect('adminhome')
#             else:
#                 messages.info(request, 'Invalid Credentials')
#                 return render(request, 'index.html')
#         else:
#             return render(request, 'index.html')


def registervidpage(request):
    return render(request, 'registervid.html')


def forgotpassword(request):
    return render(request, 'forgotpassword.html')


def forgot_password(request):
    if request.method == "POST":
        forgot_password.voter_id = request.POST['vid']
        voter = User.objects.get(username=forgot_password.voter_id)
        if voter is not None:
            v = Voters.objects.get(voterid_no=forgot_password.voter_id)
            vmobno = str(v.mobile_no)
            url = "http://2factor.in/API/V1/" + settings.TWO_FACTOR_API_KEY + "/SMS/" + vmobno + "/AUTOGEN"
            response = requests.request("GET", url)
            data = response.json()
            request.session['otp_session_data'] = data['Details']
            messages.info(request, 'an OTP has been sent to registered mobile number ending with')
            mobno = vmobno[6:]
            return render(request, 'forgotpassotp.html', {'mno': mobno})
        else:
            messages.info(request, 'Invalid Voter ID')
            return render(request, 'forgotpassword.html')


def forgotpassotp(request):
    if (request.method == "POST"):
        userotp = request.POST['otp']
        url = "http://2factor.in/API/V1/" + settings.TWO_FACTOR_API_KEY + "/SMS/VERIFY/" + request.session['otp_session_data'] + "/" + userotp
        response = requests.request("GET", url)
        data = response.json()
        if data['Status'] == "Success":
            return render(request, 'newpassword.html')
        else:
            messages.info(request, 'Invalid OTP')
            return render(request, 'forgotpassotp.html')


def setnewpassword(request):
    if request.method == "POST":
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            u = User.objects.get(username=forgot_password.voter_id)
            if u is not None:
                u.set_password(password1)
                u.save()
                messages.info(request, 'New password updated')
                return render(request, 'index.html')


def logout(request):
    auth.logout(request)
    return redirect('/')
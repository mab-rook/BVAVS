from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.conf import settings
from dotenv import load_dotenv
from twilio.rest import Client
from Digital_Voting.settings import BASE_DIR
from EC_Admin.models import Voters, Candidates, Election, Votes, Reports
from .models import Voted, Complain
from django.views.decorators.csrf import csrf_exempt


import os
import requests
import datetime
import math
import random
import cv2
import numpy as np
# import face_recognition
import base64
import pickle
from PIL import Image
import json


import phonenumbers
import pyotp
#setting up of twilio 
load_dotenv()

TWILIO_ACCOUNT_SID = 'AC1e07ed9334478ca42e10cd4007a81cbe'
TWILIO_AUTH_TOKEN = '41824d153b406bd210df7f766be56f8d'
VERIFY_SID = 'VA2fcdb2c9e812cfc8f3e60d2b4e074301'
verified_number = "(331) 225-1173"


# OTP = ''.join([str(random.randint(0, 9)) for _ in range(6)])

# facial_recognition
def compare_facial_data(captured_image_data, stored_facial_data):
    # Convert base64 encoded image data to binary
    binary_image_data = base64.b64decode(captured_image_data.split(',')[1])

    # Read the captured image from binary data
    captured_image = cv2.imdecode(np.frombuffer(binary_image_data, np.uint8), cv2.IMREAD_COLOR)

    # Convert stored facial data to numpy array
    stored_face_data = np.array(stored_facial_data.split(','), dtype=np.uint8)

    # Convert the stored facial data to image
    stored_image = stored_face_data.reshape(-1, 3)

    # Convert the image arrays to grayscale
    captured_gray = cv2.cvtColor(captured_image, cv2.COLOR_BGR2GRAY)
    stored_gray = stored_image[:, 0].reshape(stored_image.shape[0], 1)

    # Use OpenCV's template matching to compare faces
    match_score = cv2.matchTemplate(captured_gray, stored_gray, cv2.TM_CCOEFF_NORMED)
    
    # Get the maximum match score
    max_score = np.max(match_score)
    
    # Return the match score
    return max_score


# Create your views here.
def register_vid(request):
    if request.method == 'POST':
        # voter_id = request.POST.get('voter_id')
        voter_id = request.POST.get('vid')
        
        if Voters.objects.filter(voterid_no=voter_id):
            register_vid.v = Voters.objects.get(voterid_no=voter_id)
            user_phone = register_vid.v.mobile_no
        # Retrieve voter information
        # try:
        #     voter = Voters.objects.get(voterid_no=voter_id)
        # except Voters.DoesNotExist:
        #     return JsonResponse({'status': 'error', 'message': 'Voter not found'})
            
        # Generate and send OTP using Twilio Verify
            if user_phone:
                totp = pyotp.TOTP(pyotp.random_base32(), interval=300)
                otp = totp.now()
                client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                message = client.messages.create(
                    body=f'Your OTP is: {otp}',
                    from_=verified_number,
                    to=user_phone
                )
            request.session['otp'] = otp
        # Store voter ID for later verification
            request.session['vid'] = voter_id
            return render(request, 'otp.html')
    # if (request.method == 'POST'):
    #     voterid = request.POST['vid']
    #     if (User.objects.filter(username=voterid)).exists():
    #         messages.info(request, 'Voter already registered')
    #         return render(request, 'registervid.html')
    #     else:
    #         if Voters.objects.filter(voterid_no=voterid):
    #             register_vid.v = Voters.objects.get(voterid_no=voterid)
    #             user_phone = str(register_vid.v.mobile_no)
    #             url = "http://2factor.in/API/V1/" + settings.TWO_FACTOR_API_KEY + "/SMS/" + user_phone + "/AUTOGEN"
    #             response = requests.request("GET", url)
    #             data = response.json()
    #             request.session['otp_session_data'] = data['Details']
    #             messages.info(request, 'an OTP has been sent to registered mobile number ending with')
    #             mobno = user_phone[6:]
    #             return render(request, 'otp.html', {'mno': mobno})
        else:
            messages.info(request, 'Invalid Voter ID')
            return render(request, 'registervid.html')
@csrf_exempt
def otp(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        if 'otp' in request.session:
            otp_generated = request.session['otp']
            if otp_entered == otp_generated:
                return render(request, './register.html',
                            {'voterid_no': register_vid.v.voterid_no, 'name': register_vid.v.name,
                            'father_name': register_vid.v.father_name, 'gender': register_vid.v.gender,
                            'dateofbirth': register_vid.v.dateofbirth, 'address': register_vid.v.address,
                            'mobile_no': register_vid.v.mobile_no, 'state': register_vid.v.state,
                            'pincode': register_vid.v.pincode, 'parliamentary': register_vid.v.parliamentary,
                            'assembly': register_vid.v.assembly, 'voter_image': register_vid.v.voter_image})
        
        
        # Update user's verification status
        # user_profile = UserProfile.objects.get(phone_number=phone_number)
        # if verification_check.status == 'approved':
        #     user_profile.is_verified = True
        #     user_profile.save()
        #     return JsonResponse({'status': 'success'})
        # else:
        #     return JsonResponse({'status': 'error', 'message': 'Invalid OTP'})
    
    return render(request, 'otp.html')
    
    
    # if (request.method == "POST"):
    #     userotp = request.POST['otp']
    #     otp_vcheck = client.verify.v2.services(verify_sid).verification_checks.create(to=verified_number, code=userotp)

    #     url = "http://2factor.in/API/V1/" + settings.TWO_FACTOR_API_KEY + "/SMS/VERIFY/" + request.session['otp_session_data'] + "/" + userotp
    #     response = requests.request("GET", otp_vcheck)
    #     data = response.json()
    #     if data['Status'] == "Success":
    #         response_data = {'Message': 'Success'}
    #         return render(request, './register.html',
    #                       {'voterid_no': register_vid.v.voterid_no, 'name': register_vid.v.name,
    #                        'father_name': register_vid.v.father_name, 'gender': register_vid.v.gender,
    #                        'dateofbirth': register_vid.v.dateofbirth, 'address': register_vid.v.address,
    #                        'mobile_no': register_vid.v.mobile_no, 'state': register_vid.v.state,
    #                        'pincode': register_vid.v.pincode, 'parliamentary': register_vid.v.parliamentary,
    #                        'assembly': register_vid.v.assembly, 'voter_image': register_vid.v.voter_image})
    #     else:
    #         messages.info(request, 'Invalid OTP')
    #         return render(request, 'otp.html')

@csrf_exempt
def register(request):
     if request.method=="POST":
        voter_id = request.POST.get('voterid_no')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        image = request.FILES.get('profile_image')  
        try:
            v = Voters.objects.get(voterid_no=voter_id)
        except Voters.DoesNotExist:
            # Handle the case where the voter does not exist
            return HttpResponse("Voter not found. Please check your voter ID.")
        # v=Voters.objects.filter(voterid_no=voter_id).first()
        # voterid = v.voterid_no
        if password1 == password2:  
            add_user = User.objects.create_user(username=voterid, password=password1, email=email)
            # Save image data to file
            if image:
                format, imgstr = image.split(';base64,') 
                ext = format.split('/')[-1]
                filename = f'user_{add_user.id}.{ext}'
                with open(f'user_images/{filename}', 'wb') as f:
                    f.write(base64.b64decode(imgstr))
                add_user.image = f'user_images/{filename}'
                add_user.save()
                subject = 'welcome to GFG BVAVS'
                message = f'Hi {voter_id}, thank you for registering in Bvavs., Your Voter ID is {add_user.username.unique_id}'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email]
                send_mail( subject, message, email_from, recipient_list )
                messages.info(request, 'Voter Registered')
                return redirect("/vlogin")
        # if password1 == password2:
        #     add_user = User.objects.create_user(username=voter_id, password=password1, email=email, face_data=image)
        #     add_user.save()
        #     processed_image = process_image_for_recognition(image)
        
        #     # Detect faces in the processed image
        #     detected_image = detect_faces(processed_image)
        #     subject = 'welcome to GFG BVAVS'
        #     message = f'Hi {voter_id}, thank you for registering in Bvavs.'
        #     email_from = settings.EMAIL_HOST_USER
        #     recipient_list = [email]
        #     send_mail( subject, message, email_from, recipient_list )
        #     messages.info(request, 'Voter Registered')
        #     return redirect("/vlogin")
        
          #input_encodings=get_face_encoding_from_base64(input_face)

          #match=face_detect(input_encodings)
         

          #print(username,password)
          #print(input_face)
        # image=face_recognition.load_image_file(io.BytesIO(base64.b64decode(input_face)))
        # image_encoding=face_recognition.face_encodings(image)
        # encoding=image_encoding[0]
        # if(len(image_encoding)!=0):
        #     encoding = json.dumps(encoding.tolist())
        #     if password1 == password2:
        #         add_user  = v.objects.create_user(username=voter_id, password=password1, email=email, face_data=encoding)
        #         # add_user = User.objects.create_user(username=voter_id, password=password1, email=email)
        #         # add_user.save()
        #         subject = 'welcome to GFG BVAVS'
        #         message = f'Hi {voter_id}, thank you for registering in Bvavs.'
        #         email_from = settings.EMAIL_HOST_USER
        #         recipient_list = [email]
        #         send_mail( subject, message, email_from, recipient_list )
        #         messages.info(request, 'Voter Registered')
        #         return redirect("/")
            # user = User.objects.create_user(username = username, password = password)
            # UserProfile.objects.create(user = user, face_data = encoding)
            # messages.success(request, 'Profile created succesfully!')
            # print("PROfile Created Succesfully")
            # return redirect("/loginUser")
     return render(request,'signup.html')


# def register(request):
#     if (request.method == 'POST'):
#         voter_id = request.POST.get('v_id')
#         email = request.POST['email']
#         password1 = request.POST['password1']
#         password2 = request.POST['password2']
#         vidfile = request.FILES['vidfile']
#         v=Voters.objects.get(voterid_no=voter_id)
#         Id=str(v.id)
#         folder=str(BASE_DIR)+"/DatasetVideo/"
#         fs=FileSystemStorage(location=folder)
#         vidfilename=Id+vidfile.name
#         filename=fs.save(vidfilename,vidfile)
#         name=v.voterid_no
#         faceDetect = cv2.CascadeClassifier(str(BASE_DIR) + "/haarcascade_frontalface_default.xml")
#         cam = cv2.VideoCapture(folder+"/"+vidfilename)
#         sampleNum = 0
#         while (True):
#             ret, img = cam.read()
#             # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#             gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#             faces = faceDetect.detectMultiScale(gray, 1.3, 5)
#             for (x, y, w, h) in faces:
#                 cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
#                 sampleNum = sampleNum + 1
#                 cv2.imwrite(str(BASE_DIR) + "/TrainingImage/"+ name +"."+ Id + '.' + str(sampleNum) + ".jpg",gray[y:y + h, x:x + w])
#                 cv2.imshow("Face", img)
#             if cv2.waitKey(100) & 0xFF == ord('q'):
#                 break
#             elif sampleNum > 60:
#                 break
#         cam.release()
#         cv2.destroyAllWindows()

#         # Train
#         recognizer = cv2.face.LBPHFaceRecognizer_create()

#         def getImagesAndLabels(path):
#             imagePaths = [os.path.join(path, f) for f in os.listdir(path) if f != ".gitkeep"]
#             faces = []
#             Ids = []
#             for imagePath in imagePaths:
#                 pilImage = Image.open(imagePath).convert('L')
#                 imageNp = np.array(pilImage, 'uint8')
#                 Id = int(os.path.split(imagePath)[-1].split('.')[1])
#                 faces.append(imageNp)
#                 Ids.append(Id)
#             return faces, Ids
#         faces, Id = getImagesAndLabels(str(BASE_DIR) + "/TrainingImage/")
#         recognizer.train(faces, np.array(Id))
#         recognizer.save(str(BASE_DIR) + "/TrainingImageLabel/Trainner.yml")
#         if password1 == password2:
#             add_user = User.objects.create_user(username=voter_id, password=password1, email=email)
#             add_user.save()
#             subject = 'welcome to GFG BVAVS'
#             message = f'Hi {voter_id}, thank you for registering in Bvavs.'
#             email_from = settings.EMAIL_HOST_USER
#             recipient_list = [email]
#             send_mail( subject, message, email_from, recipient_list )
#             messages.info(request, 'Voter Registered')
#             return redirect("/")





# @login_required(login_url='home')
def vhome(request):
    # vhome.username = request.session['v_id']
    vhome.username = request.session['voterid_no']
    try:
        v = Voters.objects.get(voterid_no=vhome.username)
        vhome.image=v.voter_image
        return render(request,'voter/vhome.html',{'username':vhome.username,'image':vhome.image})
    except Exception as e:    
        print(e)
    # v = Voters.objects.get(voterid_no=vhome.username)
    # vhome.image=v.voter_image
    # return render(request,'voter/vhome.html',{'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vprocess(request):
    return render(request,'voter/votingprocess.html',{'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vprofile(request):
    v_id = request.session['voterid_no']
    v = Voters.objects.get(voterid_no=v_id)
    vemail = User.objects.get(username=v_id)
    return render(request, 'voter/voter profile.html', {'voterid_no': v.voterid_no, 'name': v.name,
                                                  'father_name': v.father_name, 'gender': v.gender,
                                                  'dateofbirth': v.dateofbirth, 'address': v.address,
                                                  'mobile_no': v.mobile_no, 'state': v.state,
                                                  'pincode': v.pincode, 'parliamentary': v.parliamentary,
                                                  'assembly': v.assembly, 'voter_image': v.voter_image,
                                                  'email': vemail.email,'username':v_id,'image':vhome.image})


@login_required(login_url='home')
def vchangepassword(request):
    return render(request, 'voter/vchangepassword.html',{'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vchange_password(request):
    if request.method == "POST":
        v_id = request.session['voterid_no']
        oldpass = request.POST['oldpass']
        newpass = request.POST['password1']
        newpass2 = request.POST['password2']
        u=auth.authenticate(username=v_id,password=oldpass)
        if u is not None:
            u=User.objects.get(username=v_id)
            if oldpass!=newpass:
                if newpass == newpass2:
                    u.set_password(newpass)
                    u.save()
                    messages.info(request, 'Password Changed')
                    return render(request, 'voter/vchangepassword.html',{'username':vhome.username,'image':vhome.image})
            else:
                messages.info(request, 'New password is same as old password')
                return render(request, 'voter/vchangepassword.html',{'username':vhome.username,'image':vhome.image})
        else:
            messages.info(request, 'Old Password not matching')
            return render(request, 'voter/vchangepassword.html',{'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vviewcandidate(request):
    return render(request, 'voter/view candidate.html',{'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vview_candidate(request):
    if request.method == 'POST':
        state = request.POST['states']
        constituency1 = request.POST['constituency1']
        constituency2 = request.POST['constituency2']
        if constituency1 == 'Parliamentary':
            candidates = Candidates.objects.filter(state=state, constituency=constituency1, parliamentary=constituency2)
            if candidates:
                return render(request, 'voter/view candidate.html', {'constituency':constituency2,'candidates': candidates,'username':vhome.username,'image':vhome.image})
            else:
                messages.info(request, 'No Candidate Found')
                return render(request, 'voter/view candidate.html',{'username':vhome.username,'image':vhome.image})
        else:
            candidates = Candidates.objects.filter(state=state, constituency=constituency1, assembly=constituency2)
            if candidates:
                return render(request, 'voter/view candidate.html', {'constituency':constituency2,'candidates': candidates,'username':vhome.username,'image':vhome.image})
            else:
                messages.info(request, 'No Candidate Found')
                return render(request, 'voter/view candidate.html',{'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def velection(request):
    v_id = request.session['voterid_no']
    vdetail = Voters.objects.get(voterid_no=v_id)
    status = 'active'
    if Election.objects.filter(state=vdetail.state, status=status):
        velection.e = Election.objects.get(state=vdetail.state, status=status)
        now = datetime.datetime.now()
        nowdate = now.strftime("%G-%m-%d")
        nowtime = now.strftime("%X")
        sdate = str(velection.e.start_date)
        if nowdate == sdate:
            stime = str(velection.e.start_time)
            etime = str(velection.e.end_time)
            if stime <= nowtime <= etime:
                if velection.e.election_type == 'PC-GENERAL':
                    vpc = vdetail.parliamentary
                    candidates = Candidates.objects.filter(parliamentary=vpc)
                    return render(request, 'voter/velection.html', {'candidate': candidates,'username':vhome.username,'image':vhome.image})
                elif velection.e.election_type == 'AC-GENERAL':
                    vac=vdetail.assembly
                    candidates = Candidates.objects.filter(assembly=vac)
                    return render(request, 'voter/velection.html', {'candidate': candidates,'username':vhome.username,'image':vhome.image})
            else:
                messages.info(request, 'No Elections Runnning')
                return render(request, 'voter/vnoelection.html',{'username':vhome.username,'image':vhome.image})
        else:
            messages.info(request, 'No Elections Runnning')
            return render(request, 'voter/vnoelection.html',{'username':vhome.username,'image':vhome.image})
    else:
        messages.info(request, 'No Elections Runnning')
        return render(request, 'voter/vnoelection.html',{'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vote(request):
    if request.method == "POST":
        v_id = request.session['voterid_no']
        vote.v = Voted.objects.get(election_id=velection.e.election_id,voter_id=v_id)
        if vote.v.has_voted == 'no':
            vidofv=Voters.objects.get(voterid_no=v_id)
            # detectuserid=str(vidofv.id)
            image_data = request.POST.get('image_data')
            # folder=str(BASE_DIR)+"/VotingDSVideo/"
            # fs=FileSystemStorage(location=folder)
            # vidfilename=detectuserid+vidfile.name
            # filename=fs.save(vidfilename,vidfile)
            # rec = cv2.face.LBPHFaceRecognizer_create()
            # rec.read(str(BASE_DIR)+"/TrainingImageLabel/Trainner.yml")
            # faceDetect = cv2.CascadeClassifier(str(BASE_DIR)+"/haarcascade_frontalface_default.xml")
            # cam = cv2.VideoCapture(folder+"/"+vidfilename)
            # font = cv2.FONT_HERSHEY_SIMPLEX
            # flag=0
            # unknowncount=0
            # while flag!=1 and unknowncount!=5:
            #     ret, img = cam.read()
            #     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            #     faces = faceDetect.detectMultiScale(gray, 1.3, 5)
            #     for(x,y,w,h) in faces:
            #         cv2.rectangle(img,(x,y),(x+w,y+h), (0,255,0), 2)
            #         Id,conf = rec.predict(gray[y:y+h, x:x+w])
            #         if conf<50:
            #             if str(Id)==detectuserid:
            #                 tt="Detected"
            #                 cv2.putText(img, str(tt),(x,y+h), font, 2, (0,255,0),2)
            #                 cv2.waitKey(500)
            #                 flag=1
            #         else:
            #             Id='Unknown'
            #             unknowncount+=1
            #             tt=str(Id)
            #             cv2.putText(img, str(tt),(x,y+h), font, 2, (0,0,255),2)
            #     cv2.imshow("Face",img)
            #     cv2.waitKey(1000)
            #     if(cv2.waitKey(1) == ord('q')):
            #         break
            # cam.release()
            # cv2.destroyAllWindows()
            # if flag==1:
            # knownface = np.array(json.loads(vidofv.face_data))
            # image=face_recognition.load_image_file(io.BytesIO(base64.b64decode(input_face)))
            # image_encoding=face_recognition.face_encodings(image)
            # match=face_detect(image_encoding,knownface)
            
            
            #new updated 
            facial_data = vidofv.facial_data  # Fetch stored facial data
            match_score = compare_facial_data(image_data, facial_data)
            if match_score >= 0.8:
                vote.candidateid = request.POST['can']
                vmob = Voters.objects.get(voterid_no=v_id)
                vmobno = str(vmob.mobile_no)
                url = "http://2factor.in/API/V1/" + settings.TWO_FACTOR_API_KEY + "/SMS/" + vmobno + "/AUTOGEN"
                response = requests.request("GET", url)
                data = response.json()
                request.session['otp_session_data'] = data['Details']
                response_data = {'Message': 'Success'}
                messages.info(request, 'an OTP has been sent to registered mobile number ending with')
                mobno = vmobno[6:]
                return render(request, 'voter/voteotp.html', {'mno': mobno,'username':vhome.username,'vtimage':vhome.image})
            else:
                messages.info(request, 'Face not matched')
                return render(request, 'voter/votesub.html',{'username':vhome.username,'image':vhome.image})
        else:
            messages.info(request, 'Already Voted')
            return render(request, 'voter/votesub.html',{'username':vhome.username,'image':vhome.image})


# def face_detect(reference, to_check):

#      print("Comparing With DataBAse")
#      #print(reference, to_check)
#      matches = face_recognition.compare_faces(np.array(reference),[np.array(to_check)])    
#      print("Input face Encoding")
#      print(np.array(reference))
#      print("Known User Encodings")
#      print([np.array(to_check)])
#      name = "Unknown"
#      if True in matches:
#          print("Match Found")
#          return True    
#      else:
#          return False


@login_required(login_url='home')
def subvoteotp(request):
    if (request.method == "POST"):
        userotp = request.POST['otp']
        url = "http://2factor.in/API/V1/" + settings.TWO_FACTOR_API_KEY + "/SMS/VERIFY/" + request.session['otp_session_data'] + "/" + userotp
        response = requests.request("GET", url)
        data = response.json()
        if data['Status'] == "Success":
            v_id = request.session['v_id']
            vemail=User.objects.get(username=v_id)
            email=vemail.email
            string="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            length=len(string)
            subvoteotp.otp=""
            for i in range(6):
                subvoteotp.otp+=string[math.floor(random.random()*length)]
            send_mail(
                'OTP from bvavs',
                'The following is the 6 digit alphanumeric email OTP to be entered for vote submission '+subvoteotp.otp,
                settings.EMAIL_HOST_USER,
                [email]
                )
            emailstart=email[0:3]
            emailend=email[-13:]
            emailid=emailstart+'*****'+emailend
            messages.info(request,'an 6 digit alphanumeric OTP has been sent to your registered email address ')
            return render(request, 'voter/voteemailotp.html', {'username':vhome.username,'image':vhome.image,'email':emailid})
        else:
            messages.info(request, 'Invalid OTP')
            return render(request, 'voter/voteotp.html',{'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def subvoteemailotp(request):
    if request.method=="POST":
        emailotp=request.POST['emailotp']
        if subvoteotp.otp==emailotp:
            votecan = Votes.objects.get(election_id=velection.e.election_id, candidate_id=vote.candidateid)
            votecan.online_votes += 1
            votecan.save()
            vote.v.has_voted = 'yes'
            vote.v.where_voted = 'online'
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ipaddress = x_forwarded_for.split(',')[-1].strip()
            else:
                ipaddress = request.META.get('REMOTE_ADDR')
            vote.v.ipaddress = ipaddress
            vote.v.datetime = datetime.datetime.now()
            vote.v.save()
            messages.info(request, 'Vote submitted to ')
            return render(request, 'voter/votesub.html', {'votesub': votecan.candidate_name,'username':vhome.username,'image':vhome.image})
        else:
            messages.info(request, 'Invalid OTP')
            return render(request, 'voter/voteemailotp.html',{'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vviewresult(request):
    elections = Election.objects.all()
    return render(request, 'voter/viewresult.html', {'elections': elections,'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vview_result(request):
    if request.method=="POST":
        election_id = request.POST['e_id']
        resulttype = request.POST['resulttype']
        e=Election.objects.get(election_id=election_id)
        estate=e.state
        if resulttype=="partywise":
            result = Votes.objects.filter(election_id=election_id)
            v=Votes.objects.filter(election_id=election_id)
            constituencies=[]
            for i in v:
                if i.constituency not in constituencies:
                    constituencies.append(i.constituency)
            d=[]
            for i in constituencies:
                resultcon=Votes.objects.filter(election_id=election_id,constituency=i)
                maxi=0
                for i in resultcon:
                    if i.total_votes>maxi:
                        maxi=i.total_votes
                        d.append(i.candidate_party)
            parties=[]
            for k in v:
                if k.candidate_party not in parties:
                    parties.append(k.candidate_party)
            final={}
            for i in parties:
                c=d.count(i)
                final.update({i:c})
            par=[]
            won=[]
            for k,v in final.items():
                par.append(k)
                won.append(v)
            parwon=zip(par,won)
            total=0
            for i in won:
                total+=i
            return render(request, 'voter/viewpartywise.html', {'total':total,'parwon':parwon,'electionid': election_id,'state':estate,'username':vhome.username,'image':vhome.image})
        elif resulttype=="constituencywise":
            v=Votes.objects.filter(election_id=election_id)
            constituencies=[]
            for i in v:
                if i.constituency not in constituencies:
                    constituencies.append(i.constituency)
            return render(request, 'voter/viewresultconwise.html', {'electionid':election_id,'state':estate,'constituency':constituencies,'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vview_result_filter(request):
    if request.method=="POST":
        election_id = request.POST['e_id']
        constituency = request.POST['constituency']
        e=Election.objects.get(election_id=election_id)
        estate=e.state
        v=Votes.objects.filter(election_id=election_id)
        result = Votes.objects.filter(election_id=election_id, constituency=constituency)
        constituencies=[]
        for i in v:
            if i.constituency not in constituencies:
                constituencies.append(i.constituency)
        totalvotes=0
        totalonline=0
        totalevm=0
        for i in result:
            totalvotes+=i.total_votes
            totalonline+=i.online_votes
            totalevm+=i.evm_votes
        perofvotes=[]
        for i in result:
            per=(i.total_votes/totalvotes)*100
            percentage=float("{:.2f}".format(per))
            perofvotes.append(percentage)
        finalresult=zip(result,perofvotes)
        return render(request, 'voter/viewresultconwise.html', {'totalonline':totalonline,'totalevm':totalevm,'totalvotes':totalvotes,'result':finalresult,'electionid':election_id,'state':estate,'constituency':constituencies,'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vviewreport(request):
    elections = Election.objects.all()
    return render(request, 'voter/viewreport.html', {'elections': elections,'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vview_report(request):
    election_id = request.POST['e_id']
    constituency = request.POST['constituency2']
    report = Reports.objects.filter(election_id=election_id, constituency=constituency)
    elections = Election.objects.all()
    return render(request, 'voter/viewreport.html', {'report': report, 'elections':elections,'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vcomplain(request):
    v_id = request.session['voterid_no']
    complain=Complain.objects.filter(voterid_no=v_id,viewed=True,replied=True)
    return render(request, 'voter/vcomplain.html',{'voterid_no': v_id, 'reply':complain,'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def submitcomplain(request):
    if (request.method == 'POST'):
        v_id = request.session['voterid_no']
        complain = request.POST['complain']
        addcomplain = Complain(voterid_no=v_id, complain=complain)
        addcomplain.save()
        messages.info(request, 'complain submitted')
        return render(request, 'voter/vcomplain.html',{'username':vhome.username,'image':vhome.image})
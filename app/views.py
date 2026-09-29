import cv2
import subprocess
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache, cache_control



from app.models import *

# Create your views here.
@never_cache
def home(request):
    return render(request, 'home.html')




@login_required(login_url='login')
@never_cache
def logout_user(request):
    logout(request)              # Django logout
    request.session.flush()      # Clear session
    messages.success(request, "Logged out successfully.")
    return redirect('login')     # Redirect to login page




@csrf_exempt
@never_cache
def login(request):
    if request.method == "POST":
        uname = request.POST['uname']
        password = request.POST['password']


        a = User.objects.filter(username=uname).first()
        if a:
            if uname==a.username:

                user = authenticate(request, username=uname, password=password)
                print("USER : ", user)

                if user is not None:
                    auth_login(request, user)
                    request.session['user_id'] = user.id  # Auth user ID

                    if user.groups.filter(name='admin').exists():
                        return redirect('admin_home')
                        
                    elif user.groups.filter(name='user').exists():
                        user_profile  = User_Profile.objects.get(USER=user)
                        request.session['user'] = user_profile.id
                        return redirect('user_home')
                        
                    else:
                        messages.error(request, 'Invalid username or password')
                        return redirect('login')
                else:
                    messages.error(request, 'Username or password incorrect')
            else:
                    messages.error(request, 'Invalid username')
                    return redirect('login')
            
        else:
            messages.error(request, 'No such user exist in this platform')
            return redirect('login')
    return render(request, 'login.html')




@never_cache
@csrf_exempt
def user_registration(request):
    if request.method == "POST":
        fname=request.POST['fname']
        lname=request.POST['lname']
        email=request.POST['email']
        phone=request.POST['phone']
        place=request.POST['place']
        gender=request.POST['gender']
        username=request.POST['username']
        password=request.POST['password']
       
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('user_registration')

        # Create user using Django's auth system
        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()

        try:
            group = Group.objects.get(name='user')
        except Group.DoesNotExist:
            group = Group.objects.create(name='user')
        user.groups.add(group)

        # Create care center profile
        User_Profile.objects.create(
            USER=user,
            first_name=fname,
            last_name=lname,
            email=email,
            phone=phone,
            place=place,
            gender=gender,
        )

        messages.success(request, 'Registration Completed. Please wait for the approval.')

    return render(request, 'user_registration.html')





# ------------------------------------------ ADMIN ------------------------------------------------------------------------------------



# @csrf_exempt
# @never_cache
# @cache_control(no_cache=True, must_revalidate=True, no_store=True)

@login_required(login_url='login')
@never_cache
def admin_home(request):
    a = User_Profile.objects.count()
    b = Complaint.objects.filter(reply='pending').count()
    c = Feedback.objects.count()

    d = User_Profile.objects.all().order_by('-id')[:5]


    return render(request, 'admin_home.html',{'a':a,'b':b,'c':c,'d':d})





@login_required(login_url='login')
@never_cache
def admin_view_users(request):
    a=User_Profile.objects.all()

    return render(request, 'admin_view_users.html', {'a': a})



from datetime import date
@login_required(login_url='login')
@never_cache
@csrf_exempt
def admin_view_complaints(request):
    a=Complaint.objects.all()

    if request.method == "POST":
        id = request.POST['id']
        reply = request.POST['reply']

        b = Complaint.objects.get(id=id)
        b.reply = reply
        b.save()
        messages.success(request, 'Reply Sent.')

    return render(request, 'admin_view_complaints.html',{'a': a})




@login_required(login_url='login')
@never_cache
def admin_view_feedback(request):
    a=Feedback.objects.all()

    return render(request, 'admin_view_feedback.html', {'a': a})


# ------------------------------------------ USER ------------------------------------------------------------------------------------



# @csrf_exempt
def user_home(request):
    return render(request, 'user_home.html')



from datetime import date
@login_required(login_url='login')
@never_cache
@csrf_exempt
def user_send_complaint(request):
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['desc']

        Complaint.objects.create(
            USER_PROFILE_id=request.session['user'],
            title=title,
            description=description,
            reply='pending',
            date=date.today(),
        )

        messages.success(request, 'Complaint sent successfully')

    a=Complaint.objects.filter(USER_PROFILE = request.session['user'])

    return render(request, 'user_send_complaint.html',{'a': a})


@login_required(login_url='login')
@never_cache
def user_delete_complaint(request,id):
    a=Complaint.objects.get(id=id)
    a.delete()
      
    messages.success(request, 'Complaint Deleted.')

    return redirect('user_send_complaint')




from datetime import date
@login_required(login_url='login')
@never_cache
@csrf_exempt
def user_send_feedback(request):
    if request.method == "POST":
        feedback = request.POST['feedback']

        Feedback.objects.create(
            USER_PROFILE_id=request.session['user'],
            feedback=feedback,
            date=date.today(),
        )

        messages.success(request, 'Feedback sent successfully')

    a=Feedback.objects.filter(USER_PROFILE = request.session['user'])

    return render(request, 'user_send_feedback.html',{'a': a})




@login_required(login_url='login')
@never_cache
def user_delete_feedback(request,id):
    a=Feedback.objects.get(id=id)
    a.delete()
      
    messages.success(request, 'Feedback Deleted.')

    return redirect('user_send_feedback')




#####################################   VIRTUAL MOUSE IMPLEMENTATION   ####################################################


from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
import threading
import cv2

# Global flags to control the threads
eye_control_active = False
hand_control_active = False

# Global references to video captures (to release them when stopping)
# Global references to video captures (to release them when stopping)
eye_capture = None
hand_capture = None

def eye_mouse_wrapper(cam_index=0):
    """Wrapper that checks the flag and releases resources"""
    global eye_control_active, eye_capture
    from .finalmousecontroller import start_eye_mouse
    
    try:
        # Pass the control flag and camera index to the function
        start_eye_mouse(lambda: eye_control_active, cam_index=cam_index)
    finally:
        eye_control_active = False
        if eye_capture:
            try:
                eye_capture.release()
            except Exception:
                pass
            eye_capture = None
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass

def hand_gesture_wrapper(cam_index=0):
    """Wrapper that checks the flag and releases resources"""
    global hand_control_active, hand_capture
    from .Gesture_Controller import start
    
    try:
        # Pass the control flag and camera index to the function
        start(lambda: hand_control_active, cam_index=cam_index)
    finally:
        hand_control_active = False
        if hand_capture:
            try:
                hand_capture.release()
            except Exception:
                pass
            hand_capture = None
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass

def check_available_cameras(probe_hardware=False, max_tested=4):
    """
    Detects available camera devices.
    If probe_hardware=False, uses fast Windows PnP / defaults without turning on physical camera.
    If probe_hardware=True, physically probes video capture devices.
    """
    if hasattr(cv2, 'setLogLevel'):
        try:
            cv2.setLogLevel(0)
        except Exception:
            pass

    # Try to obtain friendly device names from Windows PnP
    friendly_names = []
    try:
        cmd = ['powershell', '-NoProfile', '-Command', 'Get-PnpDevice -Class Camera, Image -Status OK | Select-Object -ExpandProperty FriendlyName']
        creation_flags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        out = subprocess.check_output(cmd, timeout=3, creationflags=creation_flags).decode()
        friendly_names = [line.strip() for line in out.splitlines() if line.strip()]
    except Exception:
        pass

    if not probe_hardware:
        available = []
        if friendly_names:
            for idx, name in enumerate(friendly_names[:max_tested]):
                available.append({'index': idx, 'name': f"Camera {idx} ({name})"})
        if not available:
            available.append({'index': 0, 'name': 'Camera 0 (Default / Built-in)'})
        return available

    available = []
    for i in range(max_tested):
        try:
            # Probe with CAP_DSHOW on Windows for instant response without freezing
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if not cap.isOpened():
                cap.release()
                cap = cv2.VideoCapture(i)
            if cap is not None and cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    if i < len(friendly_names) and friendly_names[i]:
                        label = f"Camera {i} ({friendly_names[i]})"
                    elif i == 0:
                        label = "Camera 0 (Default / Built-in)"
                    else:
                        label = f"Camera {i} (External USB {i})"
                    available.append({'index': i, 'name': label})
                cap.release()
        except Exception:
            pass

    # Ensure at least Camera 0 is represented if none opened (e.g. camera temporarily busy)
    if not available:
        label = f"Camera 0 ({friendly_names[0]})" if friendly_names else "Camera 0 (Default / Built-in)"
        available.append({'index': 0, 'name': label})

    return available

@login_required(login_url='login')
@never_cache
def mouse_control_page(request):
    """
    Renders the mouse control selection page with verified connected cameras
    """
    available_cams = check_available_cameras(probe_hardware=False)
    request.session['available_cameras'] = available_cams
    
    selected_cam = request.session.get('selected_cam_index', 0)
    avail_indices = [c['index'] for c in available_cams]
    if selected_cam not in avail_indices and avail_indices:
        selected_cam = avail_indices[0]
        request.session['selected_cam_index'] = selected_cam

    context = {
        'eye_active': eye_control_active,
        'hand_active': hand_control_active,
        'selected_cam': selected_cam,
        'available_cameras': available_cams,
    }
    return render(request, 'mouse_control.html', context)

@login_required(login_url='login')
@never_cache
def mouse_control_eye(request):
    """
    Starts the eye-controlled mouse in a background thread
    """
    global eye_control_active
    
    if eye_control_active:
        messages.warning(request, 'Eye control is already running!')
        return redirect('mouse_control_page')
    
    # Extract chosen camera index
    try:
        cam_index = int(request.GET.get('cam_index', request.POST.get('cam_index', 0)))
    except (ValueError, TypeError):
        cam_index = 0
    request.session['selected_cam_index'] = cam_index

    eye_control_active = True
    
    # Start the eye mouse thread (daemon so it closes with Django)
    t = threading.Thread(target=eye_mouse_wrapper, args=(cam_index,), daemon=True)
    t.start()
    
    messages.success(request, f'Eye-controlled mouse started on Camera {cam_index}!')
    return redirect('mouse_control_page')

@login_required(login_url='login')
@never_cache
def mouse_control_hand(request):
    """
    Starts the hand gesture-controlled mouse
    """
    global hand_control_active
    
    if hand_control_active:
        messages.warning(request, 'Hand control is already running!')
        return redirect('mouse_control_page')
    
    # Extract chosen camera index
    try:
        cam_index = int(request.GET.get('cam_index', request.POST.get('cam_index', 0)))
    except (ValueError, TypeError):
        cam_index = 0
    request.session['selected_cam_index'] = cam_index

    hand_control_active = True
    
    # Start in a thread to avoid blocking
    t = threading.Thread(target=hand_gesture_wrapper, args=(cam_index,), daemon=True)
    t.start()
    
    messages.success(request, f'Hand gesture control started on Camera {cam_index}!')
    return redirect('mouse_control_page')

@login_required(login_url='login')
@never_cache
def stop_mouse_control(request):
    """
    Stops all mouse control threads safely
    """
    global eye_control_active, hand_control_active, eye_capture, hand_capture
    from .camera_stream import stream_manager
    
    was_active = eye_control_active or hand_control_active or stream_manager.is_streaming
    
    eye_control_active = False
    hand_control_active = False
    stream_manager.stop_stream()
    
    # Release camera resources safely
    if eye_capture:
        try:
            eye_capture.release()
        except Exception:
            pass
        eye_capture = None
    if hand_capture:
        try:
            hand_capture.release()
        except Exception:
            pass
        hand_capture = None
    
    # Safely destroy any OpenCV windows without throwing error on headless/missing backends
    try:
        cv2.destroyAllWindows()
    except Exception:
        pass
    
    if was_active:
        messages.success(request, 'All camera & mouse control sessions stopped successfully!')
    else:
        messages.info(request, 'No active mouse control to stop.')
    
    return redirect('mouse_control_page')

@csrf_exempt
@login_required(login_url='login')
@never_cache
def get_available_cameras(request):
    """
    API endpoint that dynamically probes available cameras on host machine and returns JSON
    """
    cameras = check_available_cameras(max_tested=4)
    request.session['available_cameras'] = cameras
    return JsonResponse({
        'status': 'success',
        'cameras': cameras,
        'count': len(cameras)
    })

@login_required(login_url='login')
@never_cache
def video_feed(request):
    """
    In-browser MJPEG streaming endpoint for camera preview & virtual mouse detection.
    """
    from .camera_stream import stream_manager
    mode = request.GET.get('mode', 'preview').strip().lower()
    try:
        cam_index = int(request.GET.get('cam_index', 0))
    except (ValueError, TypeError):
        cam_index = 0
    enable_mouse = request.GET.get('enable_mouse', '1') in ['1', 'true', 'True', True]

    return StreamingHttpResponse(
        stream_manager.generate_frames(mode=mode, cam_index=cam_index, enable_mouse=enable_mouse),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )


@csrf_exempt
@login_required(login_url='login')
@never_cache
def stop_stream_api(request):
    """
    AJAX endpoint to safely stop the in-browser camera stream and free resources.
    """
    from .camera_stream import stream_manager
    stream_manager.stop_stream()
    return JsonResponse({'status': 'success', 'message': 'Camera stream stopped.'})

@csrf_exempt
@login_required(login_url='login')
@never_cache
def stream_status_api(request):
    """
    AJAX telemetry endpoint to display real-time FPS, detected landmarks, and gestures in the HTML page.
    """
    from .camera_stream import stream_manager
    return JsonResponse({
        'status': 'success',
        'is_streaming': stream_manager.is_streaming,
        'telemetry': stream_manager.get_telemetry()
    })

@csrf_exempt
@login_required(login_url='login')
@never_cache
def set_mouse_control_api(request):
    """
    AJAX endpoint to dynamically toggle system mouse control on/off without restarting the stream.
    """
    from .camera_stream import stream_manager
    enabled_val = request.GET.get('enabled', request.POST.get('enabled', '0'))
    enabled = enabled_val in ['1', 'true', 'True', True]
    stream_manager.set_mouse_enabled(enabled)
    return JsonResponse({
        'status': 'success',
        'mouse_enabled': stream_manager.mouse_enabled
    })

@csrf_exempt
@login_required(login_url='login')
@never_cache
def recalibrate_center_api(request):
    """
    AJAX endpoint to recalibrate the neutral head resting position for eye/head tracking.
    """
    from .camera_stream import stream_manager
    stream_manager.recalibrate_neutral()
    return JsonResponse({
        'status': 'success',
        'message': 'Neutral head center recalibrated.'
    })



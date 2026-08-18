from django.utils import timezone
import os
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.core.files.base import ContentFile as File
from django.contrib import messages 

from skin.models.profile import UserProfile
from skin.models.scan import Scan, ScanResult
from skin.models.chat import ChatSession, ChatMessage
from .api_call import start_task, poll_task, upload_image
from .forms import UserSignupForm, UserProfileForm
from .utils import overlay_images, download_image, SKIN_CONCERNS
from skin.view_functions.profile import overall_skin_profile_view, edit_skin_profile_view
from skin.ai.build_ai_context import generate_context
from skin.ai.module_selector import ModuleSelector
from skin.ai.generate_report_data import generate_report_data
from skin.reports.pdf_report import build_pdf
import json

from django.core.serializers.json import DjangoJSONEncoder
# Create your views here.

os.makedirs("temp", exist_ok=True)

def signup(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserSignupForm()

    return render(request, 'skin/signup.html', {'form': form})



def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            login(request, form.get_user())
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, 'skin/login.html', {
        'form': form
    })


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'skin/profile.html', {'form': form, 'profile': profile})

def skin_profile(request):
    return overall_skin_profile_view(request)

def edit_skin_profile(request):
    return edit_skin_profile_view(request)  # Reusing the same view for editing


def home(request):
    return render(request, 'skin/home.html')


def about(request):
    return render(request, 'skin/about.html')


@login_required
def dashboard(request):
    if request.method == "POST":
        image = request.FILES.get('image')
        skin_concern = request.POST.getlist('skin_concern')

        if not (image and skin_concern):
            messages.error(request, "Please upload an image and select at least one skin concern before scanning.")
            report_data = generate_report_data(request.user)
            return render(request, 'skin/dashboard.html', {
                "summary": report_data.get("summary", {}),
                "insights": report_data.get("insights", {}),
                "graphs": report_data.get("graphs", {}),
                "trends": report_data.get("trends", {}),
            })

        # saving the image to temporary location
        image_path = os.path.join("temp", image.name)
        with open(image_path, 'wb+') as file:
            for chunk in image.chunks():
                file.write(chunk)

        # Getting response from API
        scan = Scan.objects.create(
            user=request.user,
            original_image=image,
            selected_concern=skin_concern,
        )

        try:
            file_id = upload_image(image_path)
            print(f"File uploaded successfully. File ID: {file_id}")
            task_id = start_task(file_id, skin_concern)
            print(f"Task started successfully. Task ID: {task_id}")
            final_response = poll_task(task_id)
            print(f"Final response received: {final_response}")
            # Clean up the temporary image file
            if os.path.exists(image_path):
                os.remove(image_path)

            output = final_response.get('data', {}).get('results', {}).get('output', {})
            print("Output length:", len(output))

            skin_result = []  # initialized unconditionally

            if not output:
                raise ValueError("The skin analysis service returned no results. Please try again with a clearer photo.")

            for items in output:
                type = items.get("type")

                if type == "resize_image":
                    mask_url = items.get("mask_urls")
                    mask_url = mask_url[0] if mask_url else None

                    resize_image_download = download_image(mask_url)
                    scan.resized_image.save(
                        f"resized_image.jpg",
                        resize_image_download,
                        save=True
                    )

                elif type == "all":
                    score = items.get("score")  # Skip processing for 'all' type

                    scan.overall_score = score
                    continue

                elif type == "skin_age":
                    score = items.get("score")

                    scan.skin_age = score
                    continue
                elif type == "skin_type":
                    print("SKIN TYPE RESULT:", items)

                    skin_types = scan.skin_type or {}

                    region = items.get("region")
                    skin_type = items.get("skin_type")

                    skin_types[region] = skin_type

                    scan.skin_type = skin_types

                    print("CURRENT SKIN TYPES:", scan.skin_type)

                elif type in SKIN_CONCERNS:
                    result = ScanResult.objects.create(
                        scan=scan,
                        skin_concern=type,
                        ui_score=items.get("ui_score"),
                        raw_score=items.get("raw_score")
                    )

                    mask_url = items.get("mask_urls")
                    mask_url = mask_url[0] if mask_url else None

                    mask_image_download = download_image(mask_url)

                    result.mask_image.save(
                        f"{type}_mask.png",
                        mask_image_download,
                        save=True
                    )

            scan.save()  # Save the scan instance after updating skin_type, overall_score, and skin_age
            print("SKIN TYPE BEFORE REFRESH:", scan.skin_type)

            scan.refresh_from_db()  # Refresh the scan instance to get the latest data from the database
            print("SKIN TYPE AFTER REFRESH:", scan.skin_type)

            for result in scan.results.all():
                if not result.mask_image:
                    continue  # Skip if mask_image is not available

                concern_type = result.skin_concern
                overlay_output = overlay_images(
                    original_image_path=scan.resized_image.path,
                    mask_image_path=result.mask_image.path,
                    output_image_path=f"temp/{concern_type}_overlay.png",
                    skin_concern=concern_type
                )

                with open(overlay_output['overlay_path'], 'rb') as overlay_file:
                    data = overlay_file.read()
                    result.overlay_image.save(
                        f"{concern_type}_overlay.png",
                        File(data),
                        save=True
                    )
                os.remove(overlay_output['overlay_path'])  # Clean up the temporary overlay image file

                skin_result.append({
                    'ui_score': result.ui_score,
                    'mask_url': result.mask_image.url,
                    'raw_score': result.raw_score,
                    'type': result.skin_concern,
                    "display_name": SKIN_CONCERNS[result.skin_concern]["display_name"],
                    "mask_image_url": result.mask_image.url,
                    "overlay_image_url": result.overlay_image.url,
                })

            report_data = generate_report_data(request.user)

            return render(request, 'skin/dashboard.html', {
                'skin_result': skin_result,
                "resized_image_url": scan.resized_image.url,
                "overall_score": scan.overall_score,
                "skin_age": scan.skin_age,
                "skin_type": scan.skin_type,
                "summary": report_data.get("summary", {}),
                "insights": report_data.get("insights", {}),
                "graphs": report_data.get("graphs", {}),
                "trends": report_data.get("trends", {}),
            })

        except Exception as e:
            # Clean up the temporary image file in case of error
            if os.path.exists(image_path):
                os.remove(image_path)

            scan.delete()

            print(f"Scan failed for user {request.user.id}: {e}")
            messages.error(request, "We couldn't complete your skin analysis. Please try again in a moment.")

            report_data = generate_report_data(request.user)
            return render(request, 'skin/dashboard.html', {
                "summary": report_data.get("summary", {}),
                "insights": report_data.get("insights", {}),
                "graphs": report_data.get("graphs", {}),
                "trends": report_data.get("trends", {}),
            })

    report_data = generate_report_data(request.user)
    return render(request, 'skin/dashboard.html', {
        "summary": report_data.get("summary", {}),
        "insights": report_data.get("insights", {}),
        "graphs": report_data.get("graphs", {}),
        "trends": report_data.get("trends", {}),
    })


# Scan History and Scan Detail Views
@login_required
def scan_history(request):

    scans = (
        Scan.objects
        .filter(user=request.user)
        .prefetch_related("results")
        .order_by("-date_created")
    )

    for scan in scans:
        for result in scan.results.all():
            result.display_name = SKIN_CONCERNS.get(
                result.skin_concern,
                {}
            ).get(
                "display_name",
                result.skin_concern.replace("_", " ").title()
            )

    return render(
        request,
        "skin/scan_history.html",
        {
            "scans": scans
        }
    )

@login_required
def scan_detail(request, scan_id):

    scan = get_object_or_404(
        Scan.objects.prefetch_related("results"),
        scan_id=scan_id,
        user=request.user
    )

    results = []

    for result in scan.results.all():

        results.append({
            "skin_concern": result.skin_concern,
            "display_name": SKIN_CONCERNS.get(
                result.skin_concern,
                {}
            ).get(
                "display_name",
                result.skin_concern.replace("_", " ").title()
            ),
            "ui_score": result.ui_score,
            "mask_image": result.mask_image,
            "overlay_image": result.overlay_image,
        })

    return render(
        request,
        "skin/scan_detail.html",
        {
            "scan": scan,
            "results": results,
        }
    )


@login_required
def delete_scan(request, scan_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=405)

    scan = get_object_or_404(Scan, scan_id=scan_id, user=request.user)

    scan.delete()

    messages.success(request, "Scan deleted successfully.")

    return redirect("scan_history")


# User Analytics, insights, summary and graphs
@login_required
def dashboard_analytics(request):
    report_data = generate_report_data(request.user)
    return render(request, "skin/dashboard.html", {
        "summary": report_data.get("summary", {}),
        "insights": report_data.get("insights", {}),
        "graphs": report_data.get("graphs", {}),
        "trends": report_data.get("trends", {})
    })


def download_report(request):
    report_data = generate_report_data(request.user)
    pdf_file = build_pdf(report_data)

    response = HttpResponse(pdf_file, content_type='application/pdf')

    response['Content-Disposition'] = 'attachment; filename="skin_report.pdf"'

    return response




# Chat Views

@login_required
def chat_page(request):
    #create session_id if not exists
    sessions = ChatSession.objects.filter(user=request.user, is_deleted=False)

    return render(request, 'skin/chat.html', {'sessions': sessions})


@login_required
def new_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=405)

    session = ChatSession.objects.create(user=request.user)
    return JsonResponse({"session_id": str(session.session_id), "title": session.title})



@login_required
def chat_history(request, session_id):
    session = get_object_or_404(ChatSession, session_id=session_id, user=request.user, is_deleted=False)
    messages = session.messages.order_by('created_at').values('role', 'content', 'message_type', 'created_at')
    return JsonResponse({
        "messages": list(messages),
        "session_id": str(session.session_id),
    })

@login_required
def delete_chat(request):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=400)
    
    session_id = request.POST.get("session_id")
    session = get_object_or_404(ChatSession, session_id=session_id, user=request.user, is_deleted=False)
    session.is_deleted = True
    session.save() 

    return JsonResponse({"success": "Chat session deleted successfully."})

def build_chat_history(session, limit=8):
    messages = session.messages.order_by('-created_at')[:limit]
    history = []
    for message in reversed(messages):
        history.append({
            "role": message.role,
            "content": message.content,
        })
    return history


@login_required
def send_message(request):
    from skin.ai.chat_engine import ChatEngine
    if request.method == "POST":
        message = request.POST.get("message")
        session_id = request.POST.get("session_id")
        mode = request.POST.get("mode", "chat")

        if not message:
            return JsonResponse({"error": "Message is required."}, status=400)

        session = get_object_or_404(ChatSession, session_id=session_id, user=request.user, is_deleted=False)

        if session.title == "New Chat Session":
            if len(message) > 50:
                session.title = message[:50].rstrip() + "..."
            else:
                session.title = message
            
        session.updated_at = timezone.now()
        session.save(update_fields=["title", "updated_at"])

        ChatMessage.objects.create(
            session =session,
            role = "user",
            content = message,
        )

        try:
            response = ChatEngine().chat(session, message=message, mode=mode)
        except Exception as e:
            import traceback
            traceback.print_exc()

            return JsonResponse(
                {"error": "LuminaSkin AI couldn't process your message right now. Please try again."},
                status=500
            )

        safe_selected_context = json.loads(json.dumps(response["selected_context"], default=str))

        ChatMessage.objects.create(
            session = session,
            role = "assistant",
            content = response["response"],
            message_type = response["plan"].get("action") if isinstance(response["plan"], dict) else "text",
            metadata = {
                "plan": response["plan"],
                "selected_context": safe_selected_context
            }
        )

        return JsonResponse({
            "response": response["response"],
            "session_id": str(session.session_id),
            "title": session.title,
            "plan": response["plan"],
            "selected_context": response["selected_context"]
        }, encoder=DjangoJSONEncoder)








# Testing Views for AI and Module Selector
from pprint import pprint
@login_required
def test_ai(request):
    # This view is for testing the AI functionality
    context = generate_context(request.user)

    pprint(context)

    return JsonResponse(context)


def test_module_selector(request):
    message = request.GET.get('message', 'Whats getting worse?')

    selector = ModuleSelector()

    plan = selector.create_plan(message)

    if hasattr(plan, 'modules'):
        return JsonResponse(plan.model_dump())
    return JsonResponse(plan)


@login_required
def test_chat(request):

    message = request.GET.get(
        "message",
        "Has my skin improved?"
    )

    engine = ChatEngine()

    response = engine.chat(
        request.user,
        message,
    )

    return JsonResponse({
        "response": response
    })
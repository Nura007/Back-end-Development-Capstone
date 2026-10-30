import logging
import requests
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import LoginForm, SignUpForm
from .models import Concert, ConcertAttending

logger = logging.getLogger(__name__)


def index(request):
    return render(request, "index.html")


def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.save())
        return redirect("index")
    return render(request, "signup.html", {"form": form})


def login_view(request):
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("index")
    return render(request, "login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("index")


def songs(request):
    try:
        response = requests.get(settings.SONGS_API_URL + "/song", timeout=5)
        response.raise_for_status()
        songs_data = response.json()["songs"]
        if not isinstance(songs_data, list):
            raise ValueError("Expected a list of songs")
    except (requests.RequestException, ValueError, KeyError, TypeError):
        logger.warning("Songs service is unavailable")
        return render(request, "songs.html", {"service_error": "Songs are temporarily unavailable."}, status=503)
    return render(request, "songs.html", {"songs": songs_data})


def photos(request):
    try:
        response = requests.get(settings.PICTURES_API_URL + "/picture", timeout=5)
        response.raise_for_status()
        photo_data = response.json()
        if not isinstance(photo_data, list):
            raise ValueError("Expected a list of photos")
    except (requests.RequestException, ValueError, TypeError):
        logger.warning("Pictures service is unavailable")
        return render(request, "photos.html", {"service_error": "Photos are temporarily unavailable."}, status=503)
    page = Paginator(photo_data, 1).get_page(request.GET.get("page"))
    return render(request, "photos.html", {"photos": page.object_list, "page_obj": page})


def concerts(request):
    attendance = {}
    if request.user.is_authenticated:
        attendance = dict(ConcertAttending.objects.filter(user=request.user).values_list("concert_id", "attending"))
    rows = [{"concert": concert, "status": attendance.get(concert.pk, "-")} for concert in Concert.objects.all()]
    return render(request, "concerts.html", {"concerts": rows})


@login_required
def concert_detail(request, id):
    concert = get_object_or_404(Concert, pk=id)
    attendance = concert.attendee.filter(user=request.user).first()
    return render(request, "concert_detail.html", {
        "concert_details": concert,
        "status": attendance.attending if attendance else "-",
        "attending_choices": ConcertAttending.AttendingChoices.choices,
    })


@login_required
@require_POST
def concert_attendee(request):
    choice = request.POST.get("attendee_choice")
    concert_id = request.POST.get("concert_id", "")
    if choice not in ConcertAttending.AttendingChoices.values or not concert_id.isdigit():
        return HttpResponseBadRequest("Invalid concert or RSVP choice")
    concert = get_object_or_404(Concert, pk=int(concert_id))
    ConcertAttending.objects.update_or_create(
        concert=concert, user=request.user, defaults={"attending": choice}
    )
    return redirect("concerts")


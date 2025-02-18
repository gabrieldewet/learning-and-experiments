from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import loader
from django.urls import reverse

from api.models import WatchlistItem


def watchlist_view(request):
    if request.method == "POST":
        movie_name = request.POST.get("movie_name")
        genre = request.POST.get("genre")
        notes = request.POST.get("notes")

        WatchlistItem.objects.create(movie_name=movie_name, genre=genre, notes=notes)
        return redirect(reverse("ui:watchlist"))  # Redirect to the same page

    watchlist_items = WatchlistItem.objects.all().order_by("-created_at")
    context = {"watchlist_items": watchlist_items}
    return render(request, "ui/watchlist.html", context)


def watchlist_table_partial(request):
    watchlist_items = WatchlistItem.objects.all().order_by("-created_at")
    template = loader.get_template("ui/_watchlist_table.html")
    context = {"watchlist_items": watchlist_items}
    return HttpResponse(template.render(context, request))

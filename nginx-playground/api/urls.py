from django.urls import path

from . import views

urlpatterns = [
    path("", views.inspect_request, name="inspect-request"),
    path("movies/", views.get_update_movie, name="watchlist-retireve"),
    # path("suggest-movie/", views.WatchlistItemRetrieve.as_view(), name="watchlist-retireve"),
    # path("watched-movie/", views.WatchlistItemDetail.as_view(), name="watchlist-update"),
]

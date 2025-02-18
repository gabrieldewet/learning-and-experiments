from django.urls import path

from . import views

app_name = "ui"  # Important for namespacing URLs

urlpatterns = [
    path("watchlist/", views.watchlist_view, name="watchlist"),
    path("watchlist/table", views.watchlist_table_partial, name="watchlist_table"),
]

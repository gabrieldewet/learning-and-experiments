from celery import shared_task

from api.models import WatchlistItem


@shared_task
def update_watchlist_item_status(item_id, watched_status):
    try:
        item = WatchlistItem.objects.get(pk=item_id)
        item.watched = watched_status
        item.save()

        # Trigger HTMX update (this part is tricky and might need adjustments)
        # You can't directly trigger HTMX from the backend.  Instead, you can:
        # 1.  Use Django Channels (WebSockets) to push updates to the client.
        # 2.  Have the client periodically poll the API for changes.
        # 3.  Use Server-Sent Events (SSE).

        # For simplicity, I'll assume you're using polling in the UI.
        # The UI will periodically call the /ui/watchlist/table endpoint.

    except WatchlistItem.DoesNotExist:
        # Handle the case where the item doesn't exist
        pass

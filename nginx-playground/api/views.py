from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from .models import WatchlistItem
from .serializers import UpdateStatusSerializer, WatchlistItemSerializer

# TODO: Add these back in at some point to test generics, for now it's not readable if
# you don't know wtf you're doing
# class WatchlistItemRetrieve(generics.RetrieveAPIView):
#     queryset = WatchlistItem.objects.filter(watched=False).order_by("-created_at").get()
#     serializer_class = WatchlistItemSerializer


# class WatchlistItemDetail(generics.RetrieveUpdateAPIView):
#     queryset = WatchlistItem.objects.all()
#     serializer_class = UpdateStatusSerializer

#     def post(self, request, *args, **kwargs):
#         instance = self.get_object()

#         serializer = self.get_serializer(instance, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view("POST", "GET")
def get_update_movie(request: Request):
    if request.method == "GET":
        ...

    if request.method == "POST":
        ...

    return Response(data={"error": f"Invalid HTTP method {request.method}"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

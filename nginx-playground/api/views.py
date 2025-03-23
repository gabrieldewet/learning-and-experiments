from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from .models import WatchlistItem
from .serializers import UpdateStatusSerializer, WatchlistItemSerializer


@api_view(["POST", "GET"])
def get_update_movie(request: Request):
    if request.method == "GET":
        movies = WatchlistItem.objects.filter(watched=False).order_by("-created_at")
        for movie in movies:
            serializer = WatchlistItemSerializer(movie)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        input_serializer = UpdateStatusSerializer(data=request.data, partial=True)
        if input_serializer.is_valid():
            ...

    return Response(data={"error": f"Invalid HTTP method {request.method}"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(["GET"])
def inspect_request(request: Request):
    print(f"{request.headers=}")
    # for key, value in request.META.items():
    #     print(f"{key}: {value}")

    headers = {key: value for key, value in request.headers.items()}
    other = {key: value for key, value in request.META.items() if key.startswith("HTTP_")}

    return Response(data={"data": request.data, "other": other, "headers": headers}, status=status.HTTP_200_OK)

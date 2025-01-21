from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response


# Create your views here.
@api_view(["GET", "POST"])
def ocr_file(request: Request):
    if request.method == "GET":
        # Validate request here

        return Response({"message": "GET request received"})

    elif request.method == "POST":
        # Validate request here

        return Response({"message": "POST request received", "data": request.data})
    else:
        return Response({"message": "Invalid request method"})

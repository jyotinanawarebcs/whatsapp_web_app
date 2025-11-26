from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def test_api(request):
    data = {
        "message": "API working successfully!"
    }
    return Response(data)  # Response object automatically JSON return karta hai

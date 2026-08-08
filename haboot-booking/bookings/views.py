from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from .services import *



class LSASearchView(APIView):
    def get(self,request):
        serializer=LSASearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        results=search_lsas(
            **serializer.validated_data
        )
        response_serializer=LSASearchResultSerializer(results,many=True)
        return Response(response_serializer.data,status=status.HTTP_200_OK)
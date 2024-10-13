import csv
from datetime import datetime
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from api.models import ShowTheme, AstronomyShow, ShowSession, PlanetariumDome, Ticket, Reservation
from api.serializers.planetarium_serializers import (
    ShowThemeSerializer, AstronomyShowSerializer, ShowSessionSerializer,
    ShowSessionListSerializer, ShowSessionRetrieveSerializer,
    PlanetariumDomeSerializer, TicketSerializer, TicketListSerializer,
    ReservationSerializer, ReservationCreateSerializer, TicketRetrieveSerializer
)
from api.validators import validate_show_time

class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer

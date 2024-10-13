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


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.prefetch_related("show_theme")
    serializer_class = AstronomyShowSerializer

    def get_queryset(self):
        queryset = self.queryset
        show_theme = self.request.query_params.get("show_theme")
        title = self.request.query_params.get("title")

        if show_theme:
            queryset = queryset.filter(show_theme__name=show_theme)
        if title:
            queryset = queryset.filter(title=title)

        return queryset

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return AstronomyShowListSerializer
        return self.serializer_class

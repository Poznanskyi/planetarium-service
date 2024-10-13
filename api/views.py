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


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.select_related("astronomy_show", "planetarium_dome")

    def get_queryset(self):
        queryset = self.queryset
        filters = {
            "astronomy_show__title": self.request.query_params.get("astronomy_show"),
            "planetarium_dome__name": self.request.query_params.get("planetarium_dome"),
            "show_time__year": self.request.query_params.get("show_time_year"),
            "show_time__month": self.request.query_params.get("show_time_month"),
            "show_time__day": self.request.query_params.get("show_time_day"),
            "show_time__hour": self.request.query_params.get("show_time_hour"),
        }
        queryset = queryset.filter(**{k: v for k, v in filters.items() if v})
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        elif self.action == "retrieve":
            return ShowSessionRetrieveSerializer
        return self.serializer_class


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.select_related("astronomy_show", "planetarium_dome")

    def get_queryset(self):
        queryset = self.queryset
        filters = {
            "astronomy_show__title": self.request.query_params.get("astronomy_show"),
            "planetarium_dome__name": self.request.query_params.get("planetarium_dome"),
            "show_time__year": self.request.query_params.get("show_time_year"),
            "show_time__month": self.request.query_params.get("show_time_month"),
            "show_time__day": self.request.query_params.get("show_time_day"),
            "show_time__hour": self.request.query_params.get("show_time_hour"),
        }
        queryset = queryset.filter(**{k: v for k, v in filters.items() if v})
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return ShowSessionListSerializer
        elif self.action == "retrieve":
            return ShowSessionRetrieveSerializer
        return self.serializer_class


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        filters = {
            "name": self.request.query_params.get("name"),
            "rows": self.request.query_params.get("rows"),
            "seats_in_row": self.request.query_params.get("seats_in_row"),
        }
        queryset = queryset.filter(**{k: v for k, v in filters.items() if v})

        if rows_range := self.request.query_params.get("rows_range"):
            min_seats, max_seats = map(int, rows_range.split("-"))
            queryset = queryset.filter(rows__range=(min_seats, max_seats))

        if seats_range := self.request.query_params.get("seats_range"):
            min_seats, max_seats = map(int, seats_range.split("-"))
            queryset = queryset.filter(seats_in_row__range=(min_seats, max_seats))

        return queryset


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related("show_session", "reservation")

    def get_queryset(self):
        title = self.request.query_params.get("title")
        if title:
            return self.queryset.filter(show_session__astronomy_show__title=title)
        return self.queryset

    @method_decorator(cache_page(60 * 60 * 2))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        elif self.action == "retrieve":
            return TicketRetrieveSerializer
        return self.serializer_class


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.select_related("user")
        if user.is_staff:
            return queryset.order_by("-user")
        return queryset.filter(user=user)

    def get_serializer_class(self):
        return ReservationCreateSerializer if self.action == "create" else ReservationSerializer


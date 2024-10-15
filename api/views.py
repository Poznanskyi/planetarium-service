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
from api.models import (
    ShowTheme,
    AstronomyShow,
    ShowSession,
    PlanetariumDome,
    Ticket,
    Reservation,
    User,
)
from api.validators import validate_show_time
from api.serializers import (
    ShowThemeSerializer,
    AstronomyShowSerializer,
    ShowSessionSerializer,
    ShowSessionListSerializer,
    ShowSessionRetrieveSerializer,
    PlanetariumDomeSerializer,
    TicketSerializer,
    TicketListSerializer,
    ReservationSerializer,
    ReservationCreateSerializer,
    TicketRetrieveSerializer,
    AstronomyShowListSerializer,
)


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
        return (
            ReservationCreateSerializer
            if self.action == "create"
            else ReservationSerializer
        )


class ShowSessionUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get("file")
        if not csv_file or not csv_file.name.endswith(".csv"):
            return Response(
                {"error": "Invalid file"}, status=status.HTTP_400_BAD_REQUEST
            )

        decoded_file = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)

        sessions_created, errors = [], []

        for row in reader:
            serializer = ShowSessionSerializer(data=row)
            if serializer.is_valid():
                show_time_str = row.get("show_time")
                try:
                    show_time = datetime.strptime(show_time_str, "%Y-%m-%d %H:%M:%S")
                    validate_show_time(
                        show_time,
                        serializer.validated_data["astronomy_show"],
                        serializer.validated_data["planetarium_dome"],
                        ShowSession.objects.all(),
                    )
                    sessions_created.append(serializer.save())
                except (ValueError, ValidationError) as e:
                    errors.append(str(e))
            else:
                errors.append(serializer.errors)

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "created_sessions": ShowSessionSerializer(
                    sessions_created, many=True
                ).data
            },
            status=status.HTTP_201_CREATED,
        )


@csrf_exempt
def get_tickets_by_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = get_user_model().objects.get(email=email)
            tickets = Ticket.objects.filter(reservation_id=user.id)
            ticket_data = list(tickets.values())
            return JsonResponse({"status": "success", "data": ticket_data}, status=200)
        except User.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "User not found"}, status=404
            )
    return JsonResponse(
        {"status": "error", "message": "Invalid request method"}, status=400
    )

from rest_framework import viewsets, permissions, pagination
from .models import SongRequest
from .serializers import SongRequestSerializer

# Pagination class
class SongRequestPagination(pagination.PageNumberPagination):
    page_size = 24
    page_size_query_param = "page_size"
    max_page_size = 40

# ViewSet for SongRequest
class SongRequestViewSet(viewsets.ModelViewSet):
    serializer_class = SongRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = SongRequestPagination

    def get_queryset(self):
        """
        - If retrieving a specific song request (GET by ID), fetch from all.
        - If listing requests, fetch only the logged-in user's requests.
        """
        if self.action == "retrieve":
            return SongRequest.objects.all()
        return self.request.user.song_requests.all()

    def perform_create(self, serializer):
        """
        Assign the logged-in user when creating a new song request.
        """
        serializer.save(user=self.request.user)

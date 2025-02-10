from rest_framework import viewsets, permissions, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import SongRequest
from .serializers import SongRequestSerializer


class SongRequestPagination(pagination.PageNumberPagination):
    page_size = 24
    page_size_query_param = "page_size"
    max_page_size = 40

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

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def reopen(self, request, pk=None):
        """
        API to reopen a song request: 
        - Allows editing the description (optional).
        - Sets status to 'pending'.
        """
        song_request = get_object_or_404(SongRequest, pk=pk, user=request.user)
        
        description = request.data.get("description")
        if description:
            song_request.description = description
        
        song_request.status = "pending"
        song_request.save()
        
        return Response(SongRequestSerializer(song_request).data, status=status.HTTP_200_OK)

